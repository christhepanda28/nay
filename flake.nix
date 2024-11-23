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
          nh = pkgs.nh;
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
          buildInputs = [ nay pkgs.nh ];
        };
      }) // {
        # NixOS module
        nixosModules.default = { config, lib, pkgs, ... }: 
        let 
          cfg = config.programs.nay;
        in
        {
          options.programs.nay = {
            enable = lib.mkEnableOption "nay package installer";
            
            configPath = lib.mkOption {
              type = lib.types.str;
              default = "/etc/nixos/configuration.nix";
              description = "Path to the NixOS configuration file containing environment.systemPackages";
            };
          };

          config = lib.mkIf cfg.enable {
            environment.systemPackages = [ self.packages.${pkgs.system}.default ];
            
            environment.etc."nay/config".text = builtins.toJSON {
              inherit (cfg) configPath;
            };
          };
        };

        # Overlay
        overlays.default = final: prev: {
          nay = self.packages.${prev.system}.default;
        };
      };
}
