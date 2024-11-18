{
  description = "nay - Interactive NixOS package installer (like yay)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        nay = pkgs.callPackage ./default.nix {
          nh = pkgs.nh;  # Add nh as a dependency
        };
      in
      {
        packages = {
          default = nay;
          nay = nay;
        };

        apps = {
          default = {
            type = "app";
            program = "${self.packages.${system}.default}/bin/nay";
          };
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [ nay pkgs.nh ];  # Add nh to development shell too
        };
      }) // {
        # NixOS module
        nixosModules.default = { pkgs, ... }: {
          nixpkgs.overlays = [
            (final: prev: {
              nay = self.packages.${prev.system}.default;
            })
          ];
        };

        # Overlay
        overlays.default = final: prev: {
          nay = self.packages.${prev.system}.default;
        };
      };
}
