# 🏠 House Stress Test

How high does water have to rise before a house — or a whole neighborhood — is under water?

**Live demo:** https://pjsheini.github.io/house-stress-test/

Enter a home address or neighborhood (or click the map), drag the water-level slider, and see:

- **The property:** ground elevation, the water level that reaches the lot, the level that gets inside, and how much margin is left.
- **The neighborhood:** % of land under water, % of buildings with water inside, and a curve of damage vs. water level.
- **The map:** flooded ground shaded by depth, and 3D Overture building footprints colored dry → yard flooded → minor → major → severe.

## Data

| What | Source |
|---|---|
| Building footprints & heights | [Overture Maps](https://overturemaps.org) buildings PMTiles |
| Ground elevation | [AWS Terrain Tiles](https://registry.opendata.aws/terrain-tiles/) (Terrarium; USGS 3DEP ~10 m in the US) |
| Address search | [OpenStreetMap Nominatim](https://nominatim.org) |
| Basemap | © OpenStreetMap contributors, © CARTO |

## How it works

A "bathtub" model: each spot's ground elevation is compared to the chosen water level (above sea level). A first-floor-height setting separates "yard flooded" from "water inside."

**Limitations:** ignores levees, sea walls, drainage, waves, and whether low inland areas actually connect to the water. It's a stress test, not a flood-risk rating. Overture's hosted PMTiles are intended for exploration, not production use.

## Run locally

It's a single static file — open `index.html` in a browser, or serve the folder:

```sh
python3 -m http.server 8000
```

## Roadmap ideas

- Hydrologic connectivity (only flood areas connected to the sea/river)
- NOAA sea-level-rise and FEMA flood-zone layers
- Shareable links per address
