#!/usr/bin/env bash
echo "🪛 Running QGIS with the InaSAFE profile:"
echo "--------------------------------"
echo "Do you want to enable debug mode?"
choice=$(gum choose "🪲 Yes" "🐞 No" )
case $choice in
	"🪲 Yes") DEBUG_MODE=1 ;;
	"🐞 No") DEBUG_MODE=0 ;;
esac
# Attempt to use pyqt5webkit - build fails
#NIXPKGS_ALLOW_INSECURE=1 nix-shell -p \
#  'qgis.override { extraPythonPackages = (ps: [ ps.numpy ps.future ps.debugpy ps.pyqt5-webkit ]);}' \
#  --command "INASAFE_DEBUG=${DEBUG_MODE} qgis --profile InaSAFE"
nix-shell -p \
  'qgis.override { extraPythonPackages = (ps: [ ps.numpy ps.future ps.debugpy ]);}' \
  --command "INASAFE_DEBUG=${DEBUG_MODE} qgis --profile InaSAFE"
