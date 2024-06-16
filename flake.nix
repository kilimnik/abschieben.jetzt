{
  description = "Application packaged using poetry2nix";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable-small";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        pkgs = nixpkgs.legacyPackages.${system}.extend poetry2nix.overlays.default;

        overrides = pkgs.poetry2nix.overrides.withDefaults (pyself: pysuper: {
          pilmoji = pysuper.pilmoji.overridePythonAttrs (oldAttrs: {
            format = "setuptools";
            prePatch = ''sed -z -i "s/with open('requirements.txt') as fp:\n    requirements = fp.readlines()/requirements=\[\"Pillow\", \"emoji\"\]/" setup.py'';
          });
        });

        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
      in
      {
        packages = {
          abschieben = mkPoetryApplication {
            inherit overrides;
            projectDir = self;
          };
          default = self.packages.${system}.abschieben;
        };

        # Shell for app dependencies.
        #
        #     nix develop
        #
        # Use this shell for developing your app.
        devShells.default = pkgs.mkShell {
          inputsFrom = [ self.packages.${system}.abschieben ];
        };

        # Shell for poetry.
        #
        #     nix develop .#poetry
        #
        # Use this shell for changes to pyproject.toml and poetry.lock.
        devShells.poetry = pkgs.mkShell {
          packages = [ pkgs.poetry ];
        };
      });
}
