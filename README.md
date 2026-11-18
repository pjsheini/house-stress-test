# 🏠 House Stress Test

How high does water have to rise before a house — or a whole neighborhood — is under water?

**Live demo:** https://pjsheini.github.io/house-stress-test/

Enter a home address or neighborhood (or click the map), drag the water-level slider, and see:

- **The property:** ground elevation, the water level that reaches the lot, the level that gets inside, and how much margin is left.
- **The neighborhood:** % of land under water, % of buildings with water inside, and a curve of damage vs. water level.
- **The map:** flooded ground shaded by depth, and 3D Overture building footprints colored dry → yard flooded → minor → major → severe → behind levee.
- **Official flood maps:** the property's FEMA flood zone and 100-year flood level (with a one-click "FEMA 100-year flood" scenario), FEMA levees drawn on the map, and the share of nearby buildings in the 100-year floodplain or behind levees.

### Scenarios

| Scenario | What it models | Data |
|---|---|---|
| 🌊 **Sea / river level** | Water rising to a chosen level above sea level (sea-level rise, surge, river flood) | NOAA sea-level-rise maps or elevation only; FEMA zones & 100-year flood level |
| 🌧️ **Heavy rain** | Rain that can't drain pooling in low spots ("pluvial" flooding), even far from water | NOAA Atlas 14 rainfall for the storm you pick (2–500-year, 1 hour–3 days) + USGS 3DEP lidar terrain |
| 🌀 **Hurricane** | Storm surge for Category 1–5 at high tide, optionally plus the storm's rain | National Hurricane Center storm-surge hazard maps (SLOSH MOMs, v3) + USGS 3DEP + the rain model |

**How the rain model works:** it downloads a ~4 m USGS lidar terrain grid around the property, fills every dip to find where water collects, traces which land drains into each dip, then pours in the rain that the storm drains can't carry and the ground doesn't absorb. Drains are assumed to handle a 2-year (typical) or 10-year (good) 1-hour storm, so what floods is the storm's worst burst above that capacity. It ignores pipes, culverts and overland spill from one dip to the next, so treat it as a screening estimate.

**How the hurricane model works:** NHC maps give surge depth in classes (under 3 ft, over 3, 6 or 9 ft above ground). Surge water is nearly flat across a neighborhood, so the app finds the water level most consistent with every building's class and its USGS ground height, and reports that level and the property's depth as a range.

### Flood models (sea / river level)

| Model | What floods | Accounts for levees? |
|---|---|---|
| **NOAA · connected to sea** (default) | Only low areas hydrologically connected to the ocean, using NOAA's sea-level-rise maps (0–10 ft above local high tide, half-foot steps) | Yes — areas cut off by levees and other barriers stay dry |
| **Elevation only** | Every spot below the water level ("bathtub") | Only where FEMA marks an area as levee-protected and "Assume levees hold" is on |

Above 10 ft over high tide, or away from the coast, the NOAA model falls back to elevation only.

## Data

| What | Source |
|---|---|
| Building footprints & heights | [Overture Maps](https://overturemaps.org) buildings PMTiles |
| Ground elevation (property & buildings) | [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) ImageServer `getSamples` (lidar-based, NAVD88) |
| Flood shading on the map | [AWS Terrain Tiles](https://registry.opendata.aws/terrain-tiles/) (Terrarium) |
| Flood zones, 100-year flood elevations, levees | [FEMA National Flood Hazard Layer](https://www.fema.gov/flood-maps/national-flood-hazard-layer) (layers 28, 16, 23) |
| Sea-level-rise inundation (connected to sea) | [NOAA Sea Level Rise Viewer](https://coast.noaa.gov/slr/) map services (`dc_slr/slr_Xft`) |
| Datum conversion (NGVD29 → NAVD88, high tide → NAVD88) | [NOAA VDatum API](https://vdatum.noaa.gov/docs/services.html) |
| Rainfall amounts by storm rarity and length | [NOAA Atlas 14](https://hdsc.nws.noaa.gov/pfds/) GIS grids, repackaged into `data/atlas14/` by the **Build Atlas 14 rainfall tiles** GitHub Action (NOAA's server doesn't allow browser requests) |
| Terrain for rain ponding | [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) ImageServer `exportImage` (float GeoTIFF, read with geotiff.js) |
| Hurricane storm surge (Cat 1–5) | [NOAA National Hurricane Center storm surge hazard maps](https://www.nhc.noaa.gov/nationalsurge/) (v3 tiles) |
| Address search | [OpenStreetMap Nominatim](https://nominatim.org) |
| Basemap | © OpenStreetMap contributors, © CARTO |

## How it works

Everything is measured in feet above sea level (NAVD88). Each building's ground elevation is compared to the chosen water level; a first-floor-height setting separates "yard flooded" from "water inside." FEMA flood elevations published on the older NGVD29 datum and NOAA's high-tide-based levels are converted to NAVD88 with VDatum.

**Limitations:** no national sea-wall dataset exists, so sea walls count only where they shaped FEMA's or NOAA's own mapping. Levees can be overtopped or fail; "Assume levees hold" is a scenario switch, not a guarantee. FEMA zones are loaded for the neighborhood around the selected spot, not the whole map. The rain model doesn't see storm-drain pipes, culverts or basements, and Atlas 14 doesn't cover Washington and Oregon yet. Hurricane surge maps are near-worst-case scenarios for each category and don't include waves. It's a stress test, not an insurance or engineering rating. Overture's hosted PMTiles are intended for exploration, not production use.

## Run locally

It's a single static file — open `index.html` in a browser, or serve the folder:

```sh
python3 -m http.server 8000
```

## Roadmap ideas

- Hydrologic connectivity (only flood areas connected to the sea/river)
- Shareable links per address
