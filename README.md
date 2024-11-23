# nay

An interactive NixOS package installer inspired by Arch Linux's `yay`. Nay helps you search, preview, and install NixOS packages with ease, automatically adding them to your `configuration.nix`.

## Features

- Interactive package search and selection
- Exact match detection
- Try packages in a temporary shell before installing
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

Search and install packages:
```bash
nay package-name
```

Or start an interactive search:
```bash
nay
```

When a package is found, you can:
- Install it permanently (adds to your configuration file and rebuilds)
- Try it in a temporary shell

## Dependencies

- NixOS
- [nh](https://github.com/viperML/nh)

## License

MIT
