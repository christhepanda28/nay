#!/usr/bin/env python3
import subprocess
import re
import os
import sys
import json
import argparse
from typing import List, Tuple, Optional

def strip_ansi_codes(text: str) -> str:
    """Remove ANSI color codes from text."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def run_nh_search(query: str) -> str:
    """Run nh search command and return its output."""
    result = subprocess.run(['nh', 'search', query], capture_output=True, text=True)
    return strip_ansi_codes(result.stdout)

def parse_search_results(output: str) -> List[Tuple[str, str, str]]:
    """Parse the nh search output and return list of (package_name, version, description)."""
    packages = []
    current_package = None
    current_description = None
    
    for line in output.split('\n'):
        # Skip empty lines and headers
        if not line.strip() or "Querying" in line or "Took" in line or "Position:" in line:
            continue
            
        # Check if line starts with a package name (no indentation)
        if not line.startswith(' '):
            # Save previous package if exists
            if current_package and current_description:
                packages.append((current_package[0], current_package[1], current_description))
            
            # Parse new package line
            # Extract name and version, cleaning any ANSI codes
            match = re.match(r'^([^\s]+)\s*\(([^)]+)\)', line)

            if match:
                package_name = strip_ansi_codes(match.group(1)).strip()
                version = strip_ansi_codes(match.group(2)).strip()
                current_package = (package_name, version)
                current_description = ""
        elif line.strip().startswith('Homepage:'):
            continue
        elif current_package and line.strip():
            current_description = strip_ansi_codes(line.strip())
    
    # Add the last package
    if current_package and current_description:
        packages.append((current_package[0], current_package[1], current_description))
    
    return packages

def find_exact_match(packages: List[Tuple[str, str, str]], query: str) -> Optional[str]:
    """Find exact match for the query in package names."""
    for name, _, _ in packages:
        base_name = name.split('.')[-1]  # Get the last part of the package name
        if base_name.lower() == query.lower():
            return name
    return None

def prompt_user_selection(packages: List[Tuple[str, str, str]]) -> Optional[str]:
    """Prompt user to select a package from the list."""
    if not packages:
        print("No packages found.")
        return None
        
    print("\nAvailable packages:")
    for i, (name, version, desc) in enumerate(packages, 1):
        # Clean the package name to ensure no color codes
        clean_name = strip_ansi_codes(name).strip()
        print(f"{i}. {clean_name} ({version})")
        print(f"   {desc}")
        
    while True:
        try:
            choice = input("\nSelect a package number (or 'q' to quit): ")
            if choice.lower() == 'q':
                return None
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(packages):
                # Return clean package name
                return strip_ansi_codes(packages[choice_idx][0]).strip()
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def get_config_path() -> str:
    """Get the configuration path from nay config file or use default."""
    config_file = "/etc/nay/config"
    default_path = "/etc/nixos/configuration.nix"
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config.get("configPath", default_path)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return default_path

def add_to_configuration(package_name: str) -> bool:
    """Add package to configuration.nix."""
    config_path = get_config_path()
    
    if not os.path.exists(config_path):
        print(f"Configuration file not found: {config_path}")
        return False
    
    # Read current configuration
    try:
        with open(config_path, 'r') as f:
            config_lines = f.readlines()
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        return False
    
    # Find the systemPackages line
    target_line = None
    for i, line in enumerate(config_lines):
        if "environment.systemPackages = with pkgs; [" in line:
            target_line = i
            break
    
    if target_line is None:
        print(f"Could not find environment.systemPackages in {config_path}")
        return False
    
    # Check if package is already in the configuration
    for line in config_lines[target_line:]:
        if package_name in line:
            print(f"Package {package_name} is already in {config_path}")
            return False
    
    # Add the package
    config_lines.insert(target_line + 1, f"    {package_name}\n")
    
    # Write back to file
    try:
        with open(config_path, 'w') as f:
            f.writelines(config_lines)
        return True
    except Exception as e:
        print(f"Error writing to configuration file: {e}")
        return False

def spawn_temp_shell(package_name: str):
    """Spawn a temporary shell with the package installed."""
    print(f"\nStarting temporary shell with {package_name}...")
    os.execvp('nix-shell', ['nix-shell', '-p', package_name])

def rebuild_system() -> bool:
    """Rebuild the system using nh os switch."""
    config_path = get_config_path()
    config_dir = os.path.dirname(config_path)
    
    print("\nRebuilding system...")
    process = subprocess.Popen(['nh', 'os', 'switch', config_dir], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.STDOUT,
                             text=True,
                             bufsize=1)
    
    # Print output in real-time
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.rstrip())
            
    return process.returncode == 0
def get_installed_packages(config_path: str) -> List[str]:
    """Extract list of installed packages from configuration.nix."""
    try:
        with open(config_path, 'r') as f:
            content = f.read()
            
        # Find the systemPackages section
        match = re.search(r'environment\.systemPackages\s*=\s*with\s+pkgs;\s*\[(.*?)\]', 
                         content, re.DOTALL)
        if not match:
            return []
            
        packages_section = match.group(1)
        # Extract package names, handling both single-line and multi-line formats
        packages = []
        for line in packages_section.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove any trailing comments
                line = line.split('#')[0].strip()
                packages.append(line)
                
        return [pkg for pkg in packages if pkg]  # Filter out empty strings
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        return []

def remove_package(package_name: str, config_path: str) -> bool:
    """Remove a package from configuration.nix."""
    try:
        with open(config_path, 'r') as f:
            lines = f.readlines()
            
        # Find the systemPackages section
        start_idx = None
        end_idx = None
        bracket_count = 0
        
        for i, line in enumerate(lines):
            if 'environment.systemPackages = with pkgs; [' in line:
                start_idx = i
                bracket_count += 1
            elif start_idx is not None:
                bracket_count += line.count('[') - line.count(']')
                if bracket_count == 0:
                    end_idx = i
                    break
        
        if start_idx is None or end_idx is None:
            print("Could not find systemPackages section")
            return False
            
        # Remove the package line
        package_removed = False
        i = start_idx + 1
        while i < end_idx:
            line = lines[i]
            if package_name in line and not line.strip().startswith('#'):
                lines.pop(i)
                end_idx -= 1
                package_removed = True
            else:
                i += 1
                
        if not package_removed:
            print(f"Package {package_name} not found in configuration")
            return False
            
        # Write back to file
        with open(config_path, 'w') as f:
            f.writelines(lines)
            
        return True
        
    except Exception as e:
        print(f"Error modifying configuration file: {e}")
        return False

def select_package_with_fzf(packages: List[str]) -> Optional[str]:
    """Use fzf to select a package from the list."""
    if not packages:
        print("No packages found in configuration")
        return None
        
    try:
        # Create fzf process
        fzf = subprocess.Popen(['fzf', '--height=50%', '--layout=reverse'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             text=True)
                             
        # Send packages to fzf
        packages_str = '\n'.join(packages)
        stdout, stderr = fzf.communicate(input=packages_str)
        
        if fzf.returncode == 130:  # User canceled
            return None
            
        if fzf.returncode == 0:
            return stdout.strip()
            
    except FileNotFoundError:
        print("Error: fzf is not installed. Please install fzf first.")
    except Exception as e:
        print(f"Error running fzf: {e}")
        
    return None

def main():
    parser = argparse.ArgumentParser(description='Interactive NixOS package installer/remover')
    parser.add_argument('action', nargs='?', choices=['install', 'remove'], 
                       help='Action to perform (install or remove)')
    parser.add_argument('query', nargs='?', help='Package to search for (only for install)')
    args = parser.parse_args()
    
    if args.action == 'remove':
        config_path = get_config_path()
        installed_packages = get_installed_packages(config_path)
        selected_package = select_package_with_fzf(installed_packages)
        
        if selected_package:
            if remove_package(selected_package, config_path):
                print(f"Removed {selected_package} from configuration.nix")
                if rebuild_system():
                    print("System successfully rebuilt!")
                else:
                    print("Failed to rebuild system")
            else:
                print("Failed to update configuration.nix")
        return
        
    query = args.query if args.query else input("Enter package name to search: ")
    # Run search
    search_output = run_nh_search(query)
    packages = parse_search_results(search_output)
    
    if not packages:
        print("No packages found.")
        return
    
    # Try to find exact match
    exact_match = find_exact_match(packages, query)
    
    # Get package to install
    package_to_install = None
    if exact_match:
        print(f"Found exact match: {exact_match}")
        while True:
            choice = input("Install this package? ([y]es/[n]o/[t]mp shell): ").lower()
            if choice in ['y', 'n', 't']:
                if choice == 'y':
                    package_to_install = exact_match
                elif choice == 't':
                    spawn_temp_shell(exact_match)
                    return
                break
            print("Please enter 'y', 'n', or 't'")
    else:
        package_to_install = prompt_user_selection(packages)
        if package_to_install:
            while True:
                choice = input("Install this package? ([y]es/[n]o/[t]mp shell): ").lower()
                if choice in ['y', 'n', 't']:
                    if choice == 't':
                        spawn_temp_shell(package_to_install)
                        return
                    elif choice == 'n':
                        package_to_install = None
                    break
                print("Please enter 'y', 'n', or 't'")
    
    if package_to_install:
        if add_to_configuration(package_to_install):
            print(f"Added {package_to_install} to configuration.nix")
            if rebuild_system():
                print("System successfully rebuilt!")
            else:
                print("Failed to rebuild system")
        else:
            print("Failed to update configuration.nix")

if __name__ == "__main__":
    main()
