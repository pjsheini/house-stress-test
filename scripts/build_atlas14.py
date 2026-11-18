#!/usr/bin/env python3
"""
Build compact NOAA Atlas 14 rainfall tiles for the House Stress Test web app.

NOAA's Precipitation Frequency Data Server doesn't allow browser (CORS) requests,
so this script runs in GitHub Actions, downloads the official Atlas 14 GIS grids
(ArcInfo ASCII, 30 arc-second, values in 1/1000 inch), resamples them to a
0.05-degree lattice and writes 5x5-degree binary tiles the page can fetch
from the same origin.

Output (data/atlas14/):
  index.json                       grid order, units, tile list
  t_{lat0}_{lon0}.bin              uint16 little-endian, shape [grids][100][100],
                                   row 0 = north edge, hundredths of an inch,
                                   65535 = no data
"""
import io, json, os, re, sys, time, zipfile, urllib.request
import numpy as np

BASE = "https://hdsc.nws.noaa.gov/pub/hdsc/data/"
ARIS = [2, 10, 25, 100, 500]
DURS = ["01h", "06h", "24h", "03d"]          # 1 hour, 6 hours, 24 hours, 3 days
CELL = 0.05
TILE = 5.0
N = int(round(TILE / CELL))                 # 100 cells per tile side
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "atlas14")
NODATA = 65535


def get(url, binary=False, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "house-stress-test (github.com/pjsheini/house-stress-test)"})
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except Exception as e:
            print(f"  retry {i+1} {url}: {e}", flush=True)
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"failed: {url}")


def list_dir(url):
    html = get(url)
    return sorted(set(re.findall(r'href="([^"?/][^"]*)"', html)))


def parse_asc(raw):
    text = raw.decode("ascii", "replace")
    header, i = {}, 0
    lines = text.split("\n", 7)
    for ln in lines[:6]:
        k, v = ln.split()[:2]
        header[k.lower()] = float(v)
    body = lines[6] + ("\n" + lines[7] if len(lines) > 7 else "")
    ncols, nrows = int(header["ncols"]), int(header["nrows"])
    arr = np.fromstring(body, sep=" ", dtype=np.float32)
    arr = arr[: ncols * nrows].reshape(nrows, ncols)
    cs = header["cellsize"]
    x0 = header.get("xllcorner", header.get("xllcenter", 0) - cs / 2)
    y0 = header.get("yllcorner", header.get("yllcenter", 0) - cs / 2)
    nod = header.get("nodata_value", -9)
    return arr, x0, y0, cs, nod


def main():
    os.makedirs(OUT, exist_ok=True)
    regions = [d.rstrip("/") for d in list_dir(BASE) if d.endswith("/")]
    print("regions:", regions, flush=True)
    grids = [(a, d) for d in DURS for a in ARIS]
    tiles = {}   # (lat0, lon0) -> uint16 array [len(grids), N, N]
    pat = re.compile(r"^([a-z]+)(\d+)yr(\d+[mhd])a\.zip$")

    for reg in regions:
        try:
            files = list_dir(BASE + reg + "/")
        except Exception as e:
            print("skip region", reg, e); continue
        avail = {}
        for f in files:
            m = pat.match(f)
            if m:
                avail[(int(m.group(2)), m.group(3))] = f
        print(f"{reg}: {len(avail)} matching grids", flush=True)
        for gi, (ari, dur) in enumerate(grids):
            f = avail.get((ari, dur))
            if not f:
                continue
            print(f"  {reg} {ari}yr {dur} <- {f}", flush=True)
            z = zipfile.ZipFile(io.BytesIO(get(BASE + reg + "/" + f, binary=True)))
            asc = [n for n in z.namelist() if n.lower().endswith((".asc", ".txt"))]
            if not asc:
                print("   no ascii grid in", z.namelist()); continue
            arr, x0, y0, cs, nod = parse_asc(z.read(asc[0]))
            nrows, ncols = arr.shape
            west, south = x0, y0
            east, north = x0 + ncols * cs, y0 + nrows * cs
            # tiles overlapping this grid
            for lat0 in np.arange(np.floor(south / TILE) * TILE, north, TILE):
                for lon0 in np.arange(np.floor(west / TILE) * TILE, east, TILE):
                    lats = lat0 + TILE - (np.arange(N) + 0.5) * CELL      # north -> south
                    lons = lon0 + (np.arange(N) + 0.5) * CELL
                    r = np.floor((north - lats) / cs).astype(int)
                    c = np.floor((lons - west) / cs).astype(int)
                    rv, cv = (r >= 0) & (r < nrows), (c >= 0) & (c < ncols)
                    if not rv.any() or not cv.any():
                        continue
                    sub = np.full((N, N), np.nan, np.float32)
                    rr, cc = np.where(rv)[0], np.where(cv)[0]
                    vals = arr[np.ix_(r[rr], c[cc])]
                    vals = np.where((vals == nod) | (vals < 0), np.nan, vals)
                    sub[np.ix_(rr, cc)] = vals
                    if np.isnan(sub).all():
                        continue
                    key = (int(lat0), int(lon0))
                    t = tiles.setdefault(key, np.full((len(grids), N, N), NODATA, np.uint16))
                    hund = np.round(sub / 10.0)                      # 1/1000 in -> 1/100 in
                    fill = (t[gi] == NODATA) & ~np.isnan(hund)
                    t[gi][fill] = np.clip(hund[fill], 0, 65534).astype(np.uint16)

    names = []
    for (lat0, lon0), t in sorted(tiles.items()):
        if (t == NODATA).all():
            continue
        name = f"t_{lat0}_{lon0}.bin"
        t.astype("<u2").tofile(os.path.join(OUT, name))
        names.append([lat0, lon0])
    idx = {
        "source": "NOAA Atlas 14 precipitation frequency estimates (PDS, mean), hdsc.nws.noaa.gov",
        "built": time.strftime("%Y-%m-%d"),
        "cell_deg": CELL, "tile_deg": TILE, "n": N, "units": "0.01 inch", "nodata": NODATA,
        "layout": "uint16 LE [grid][row north->south][col west->east]",
        "grids": [{"ari_years": a, "duration": d} for a, d in grids],
        "tiles": names,
    }
    with open(os.path.join(OUT, "index.json"), "w") as fh:
        json.dump(idx, fh)
    print(f"wrote {len(names)} tiles", flush=True)
    if not names:
        sys.exit("no tiles produced")


if __name__ == "__main__":
    main()
