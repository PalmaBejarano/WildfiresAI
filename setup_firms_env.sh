#!/bin/zsh
# === setup_firms_env.sh ===
# Configure FIRMS endpoints as conda env variables (32 total: 8 regions × 4 feeds).
# Base format:
#   https://firms.modaps.eosdis.nasa.gov/api/area/csv/${FIRMS_MAP_KEY}/${SOURCE}/${BBOX|world}/${DAYS}

set -euo pipefail

: "${FIRMS_MAP_KEY:?FIRMS_MAP_KEY is not set. Export it first (or load it from your local .env).}"

if ! command -v conda >/dev/null 2>&1; then
  echo "conda not found. Please run this in a shell where conda is available."
  exit 1
fi

conda activate base >/dev/null 2>&1 || true

mk_firms_4 () {
  local REGION="$1"
  local BBOX="$2"

  conda env config vars set "FIRMS_VIIRS_${REGION}_24H=https://firms.modaps.eosdis.nasa.gov/api/area/csv/${FIRMS_MAP_KEY}/VIIRS_SNPP_NRT/${BBOX}/1"
  conda env config vars set "FIRMS_VIIRS_${REGION}_7D=https://firms.modaps.eosdis.nasa.gov/api/area/csv/${FIRMS_MAP_KEY}/VIIRS_SNPP_NRT/${BBOX}/7"
  conda env config vars set "FIRMS_MODIS_${REGION}_24H=https://firms.modaps.eosdis.nasa.gov/api/area/csv/${FIRMS_MAP_KEY}/MODIS_NRT/${BBOX}/1"
  conda env config vars set "FIRMS_MODIS_${REGION}_7D=https://firms.modaps.eosdis.nasa.gov/api/area/csv/${FIRMS_MAP_KEY}/MODIS_NRT/${BBOX}/7"
}

mk_firms_4 GLOBAL           "world"
mk_firms_4 AFRICA           "-20,-35,55,38"
mk_firms_4 ASIA             "26,-10,180,82"
mk_firms_4 EUROPE           "-31,27,40,72"
mk_firms_4 NORTH_AMERICA    "-170,5,-50,83"
mk_firms_4 SOUTH_AMERICA    "-85,-57,-32,14"
mk_firms_4 CENTRAL_AMERICA  "-118,5,-77,33"
mk_firms_4 AUSTRALIA_NZ     "110,-50,180,0"

echo "FIRMS variables configured in conda env: $(conda env config vars list | grep '^FIRMS_' | wc -l | tr -d ' ')"



