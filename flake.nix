{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, poetry2nix }:
    let
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: (import nixpkgs {
        inherit system;
        overlays = [
          poetry2nix.overlay
        ];
      }));

      overrides = pkgs: pkgs.poetry2nix.overrides.withDefaults (pyself: pysuper: {
        pilmoji = pysuper.pilmoji.overridePythonAttrs (oldAttrs: {
          format = "setuptools";
          prePatch = ''sed -z -i "s/with open('requirements.txt') as fp:\n    requirements = fp.readlines()/requirements=\[\"Pillow\", \"emoji\"\]/" setup.py'';
        });
      });
    in
    {
      packages = forAllSystems
        (system: {
          default = pkgs.${system}.poetry2nix.mkPoetryApplication {
            projectDir = ./.;
            overrides = overrides pkgs.${system};
          };
        });
      devShells = forAllSystems (system: {
        default = pkgs.${system}.mkShell {
          buildInputs = with pkgs.${system}; [
            poetry
            zlib
            (pkgs.${system}.poetry2nix.mkPoetryEnv {
              projectDir = ./.;
              overrides = overrides pkgs.${system};
              #   editablePackageSources = { };
            })
          ];
        };
      });
    };
}
