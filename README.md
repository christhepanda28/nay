# nay

An interactive NixOS package installer inspired by Arch Linux's `yay`. Nay helps you search, preview, install, and remove NixOS packages with ease, automatically managing them in your `configuration.nix`.

## Features

- Interactive package search and selection
- Exact match detection
- Try packages in a temporary shell before installing
- Interactive package removal using fuzzy search
- Automatic configuration file updates
- System rebuild automation
- Configurable configuration file path

## Installation

Add nay to your NixOS configuration using Flakes:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nay.url = "github:christhepanda28/nay";
  };

  outputs = { self, nixpkgs, nay, ... }: {
    nixosConfigurations.your-hostname = nixpkgs.lib.nixosSystem {
      # ...
      modules = [
        # ...
        nay.nixosModules.default
        {
          programs.nay = {
            enable = true;
            # Optional: specify a custom configuration file path
            # configPath = "/path/to/your/configuration.nix";
          };
        }
      ];
    };
  };
}
```

## Configuration

Nay can be configured through NixOS module options:

- `programs.nay.enable`: Enable/disable nay (boolean)
- `programs.nay.configPath`: Path to your NixOS configuration file containing `environment.systemPackages` (default: "/etc/nixos/configuration.nix")

## Usage

### Installing Packages

Search and install packages:
```bash
nay install package-name
# or simply
nay package-name
```

Or start an interactive search:
```bash
nay install
# or simply
nay
```

When a package is found, you can:
- Install it permanently (adds to your configuration file and rebuilds)
- Try it in a temporary shell

### Removing Packages

To remove a package:
```bash
nay remove
```

This will:
1. Show an interactive fuzzy-search list of installed packages
2. Let you select a package to remove
3. Remove it from your configuration and rebuild the system

## Dependencies

- NixOS
- [nh](https://github.com/viperML/nh)
- [fzf](https://github.com/junegunn/fzf)

## License

MIT
