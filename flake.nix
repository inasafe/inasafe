# SPDX-FileCopyrightText: Kartoza
# SPDX-License-Identifier: GPL-3.0-only
{
  description = "NixOS developer environment for the InaSAFE QGIS plugin.";
  # Pinned nixpkgs revision known to build qgis / qgis-ltr from cache.nixos.org
  # rather than compiling from source on every machine.
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/b4f4a5cf27a0eb848c6212be746a0a718f3bb019";

  outputs =
    {
      self,
      nixpkgs,
    }:
    let
      system = "x86_64-linux";
      profileName = "INASAFE";
      pkgs = import nixpkgs {
        inherit system;
        config = {
          allowUnfree = true;
        };
      };

      # InaSAFE's safe/ package is a long-lived codebase written against the
      # Qt5/PyQt5 QGIS 3.x API (CI currently tests release-3_10 .. release-3_20).
      # qgis-ltr (3.44.x, Qt5/PyQt5) is the closer match; qgis (4.x, Qt6/PyQt6)
      # is exposed too for forward-compatibility testing, but is NOT default.
      extraPythonPackages = ps: [
        ps.numpy
        ps.gdal
        ps.mock
        ps.deepdiff
        ps.debugpy
        ps.psutil
      ];
      qgisLtrWithExtras = pkgs.qgis-ltr.override {
        extraPythonPackages = ps: (extraPythonPackages ps) ++ [ ps.pyqtwebengine ];
      };
      qgisWithExtras = pkgs.qgis.override {
        extraPythonPackages = ps: (extraPythonPackages ps) ++ [ ps.pyqt6-webengine ];
      };
    in
    {
      packages.${system} = {
        default = qgisLtrWithExtras;
        qgis-ltr = qgisLtrWithExtras;
        qgis = qgisWithExtras;
      };

      apps.${system} = {
        qgis-ltr = {
          type = "app";
          program = "${qgisLtrWithExtras}/bin/qgis";
          args = [
            "--profile"
            "${profileName}"
          ];
        };
        qgis = {
          type = "app";
          program = "${qgisWithExtras}/bin/qgis";
          args = [
            "--profile"
            "${profileName}"
          ];
        };
      };

      devShells.${system} = {
        # Lightweight shell for CI lint-only jobs (pep257/flake8 equivalents).
        # Excludes QGIS/Qt/GDAL — pulling those for a job that just lints
        # triggers unnecessary cache.nixos.org download volume.
        minimal = pkgs.mkShell {
          packages = [
            pkgs.bash
            pkgs.git
            pkgs.python3
            pkgs.actionlint
            pkgs.markdownlint-cli
            pkgs.yamllint
            pkgs.pre-commit
            (pkgs.python3.withPackages (
              ps: with ps; [
                black
                flake8
                flake8-docstrings
                isort
                pydocstyle
              ]
            ))
          ];
        };

        default = pkgs.mkShell {
          packages = [
            qgisLtrWithExtras
            pkgs.actionlint
            pkgs.chafa
            pkgs.docker
            pkgs.docker-compose
            pkgs.gdb
            pkgs.git
            pkgs.glow
            pkgs.jq
            pkgs.markdownlint-cli
            pkgs.pre-commit
            pkgs.yamllint
            pkgs.yamlfmt
            (pkgs.python3.withPackages (
              ps: with ps; [
                black
                click
                debugpy
                flake8
                flake8-docstrings
                pydocstyle
                isort
                mock
                deepdiff
                numpy
                gdal
                pip
                setuptools
                wheel
                venvShellHook
                virtualenv
                pyqt5
                pyqtwebengine
              ]
            ))
          ];
          shellHook = ''
            unset SOURCE_DATE_EPOCH

            # Recreate .venv whenever the nix python it was built from changes.
            PY_INTERP="$(command -v python3)"
            if [ -d ".venv" ] && [ "$(cat .venv/.nix-python 2>/dev/null)" != "$PY_INTERP" ]; then
              echo "Python toolchain changed — recreating .venv"
              rm -rf .venv
            fi

            if [ ! -d ".venv" ]; then
              python -m venv .venv
              echo "$PY_INTERP" > .venv/.nix-python
            fi

            source .venv/bin/activate
            pip install --upgrade pip > /dev/null

            if [ -f REQUIREMENTS.txt ]; then
              pip install -r REQUIREMENTS.txt > .pip-install.log 2>&1 \
                || echo "❌ pip install REQUIREMENTS.txt failed, see .pip-install.log"
            fi
            if [ -f REQUIREMENTS_TESTING.txt ]; then
              pip install -r REQUIREMENTS_TESTING.txt >> .pip-install.log 2>&1 \
                || echo "❌ pip install REQUIREMENTS_TESTING.txt failed, see .pip-install.log"
            fi

            pre-commit install --install-hooks > /dev/null 2>&1 || true

            export PYTHONPATH="${qgisLtrWithExtras}/share/qgis/python:$PYTHONPATH"
          '';
        };
      };
    };
}
