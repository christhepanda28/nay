# nay

An interactive NixOS package installer inspired by Arch Linux's `yay`. Nay helps you search, preview, and install NixOS packages with ease, automatically adding them to your `configuration.nix`.

## Features

- Interactive package search and selection
- Exact match detection
- Try packages in a temporary shell before installing
- Automatic `configuration.nix` updates
- System rebuild automation

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
                ({pkgs, ...}: {
          environment.systemPackages = [
            nay.packages.x86_64-linux.nay
          ];
        })

      ];
    };
  };
}
```

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
- Install it permanently (adds to `configuration.nix` and rebuilds)
- Try it in a temporary shell
- Browse other options if it's not what you wanted

## Dependencies

- NixOS
- [nh](https://github.com/viperML/nh)

## License

MIT
