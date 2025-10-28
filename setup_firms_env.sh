#!/bin/zsh
# === setup_firms_env.sh ===
# Define 32 FIRMS env vars (8 regiones × 4 feeds) con el formato nuevo:
# /api/area/csv/${FIRMS_MAP_KEY}/${SOURCE}/${BBOX|world}/${DAYS}

conda activate base
export FIRMS_MAP_KEY="27f8d7a213b737284b155923ba7dd642"

function mk_firms_4() {
  local REGION=$1
  local BBOX=$2
  # VIIRS (Suomi-NPP, NRT)
  conda env config vars set FIRMS_VIIRS_${REGION}_24H="https://firms.modaps.eosdis.nasa.gov/api/area/csv/${FIRMS_MAP_KEY}/VIIRS_SNPP_NRT/${BBOX}/1"
  conda env config vars set FIRMS_VIIRS_${REGION}_7D="https://firms.modaps.eosdis.nasa.gov/api/area/csv/${FIRMS_MAP_KEY}/VIIRS_SNPP_NRT/${BBOX}/7"
  # MODIS (NRT)
  conda env config vars set FIRMS_MODIS_${REGION}_24H="https://firms.modaps.eosdis.nasa.gov/api/area/csv/${FIRMS_MAP_KEY}/MODIS_NRT/${BBOX}/1"
  conda env config vars set FIRMS_MODIS_${REGION}_7D="https://firms.modaps.eosdis.nasa.gov/api/area/csv/${FIRMS_MAP_KEY}/MODIS_NRT/${BBOX}/7"
}

# Regiones (BBOX amplios por continente)
mk_firms_4 GLOBAL "world"
mk_firms_4 AFRICA "-20,-35,55,38"
mk_firms_4 ASIA "26,-10,180,82"
mk_firms_4 EUROPE "-31,27,40,72"
mk_firms_4 NORTH_AMERICA "-170,5,-50,83"
mk_firms_4 SOUTH_AMERICA "-85,-57,-32,14"
mk_firms_4 CENTRAL_AMERICA "-118,5,-77,33"
mk_firms_4 AUSTRALIA_NZ "110,-50,180,0"

conda deactivate
conda activate base
echo "✅ FIRMS variables configuradas."
conda env config vars list | grep '^FIRMS_' | wc -l

