# 🏠 House Stress Test

How high does water have to rise before a house — or a whole neighborhood — is under water?

**Live demo:** https://pjsheini.github.io/house-stress-test/

Enter a home address or neighborhood (or click the map), drag the water-level slider, and see:

- **The property:** ground elevation, the water level that reaches the lot, the level that gets inside, and how much margin is left.
- **The neighborhood:** % of land under water, % of buildings with water inside, and a curve of damage vs. water level.
- **The map:** flooded ground shaded by depth, and 3D Overture building footprints colored dry → yard flooded → minor → major → severe → behind levee.
- **Official flood maps:** the property's FEMA flood zone and 100-year flood level (with a one-click "FEMA 100-year flood" scenario), FEMA levees drawn on the map, and the share of nearby buildings in the 100-year floodplain or behind levees.

### Flood models

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
| Address search | [OpenStreetMap Nominatim](https://nominatim.org) |
| Basemap | © OpenStreetMap contributors, © CARTO |

## How it works

Everything is measured in feet above sea level (NAVD88). Each building's ground elevation is compared to the chosen water level; a first-floor-height setting separates "yard flooded" from "water inside." FEMA flood elevations published on the older NGVD29 datum and NOAA's high-tide-based levels are converted to NAVD88 with VDatum.

**Limitations:** no national sea-wall dataset exists, so sea walls count only where they shaped FEMA's or NOAA's own mapping. Levees can be overtopped or fail; "Assume levees hold" is a scenario switch, not a guarantee. FEMA zones are loaded for the neighborhood around the selected spot, not the whole map. Ignores rainfall, drainage and waves (except where FEMA V zones include waves). It's a stress test, not an insurance or engineering rating. Overture's hosted PMTiles are intended for exploration, not production use.

## Run locally

It's a single static file — open `index.html` in a browser, or serve the folder:

```sh
python3 -m http.server 8000
```

## Roadmap ideas

- Hydrologic connectivity (only flood areas connected to the sea/river)
- Shareable links per address
