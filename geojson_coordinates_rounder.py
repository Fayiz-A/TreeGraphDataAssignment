"""
Round coordinate precision in an Esri JSON polyline export (Ontario road
network) to shrink file size, without materially affecting road-segment
distinguishability.

This does NOT simplify geometry (no vertex removal) — it only reduces
decimal precision on existing coordinates. Safe for use cases like
"click to select/remove a road segment" where adjacent-road spacing
is on the order of meters, not centimeters.
"""

import orjson
import os


def round_coords(paths: list, decimals: int) -> list:
    """Recursively round every [lon, lat] pair in an Esri JSON 'paths' array."""
    return [
        [
            [round(coord, decimals) for coord in point]
            for point in path
        ]
        for path in paths
    ]


def shrink_geojson(input_path: str, output_path: str, decimals: int = 6) -> None:
    with open(input_path, "rb") as f:
        data = orjson.loads(f.read())

    features = data.get("features", [])
    for feature in features:
        geometry = feature.get("geometry")
        if geometry and "paths" in geometry:
            geometry["paths"] = round_coords(geometry["paths"], decimals)

    with open(output_path, "wb") as f:
        f.write(orjson.dumps(data))

    before = os.path.getsize(input_path)
    after = os.path.getsize(output_path)
    print(f"Input:  {before / 1e6:.1f} MB")
    print(f"Output: {after / 1e6:.1f} MB")
    print(f"Reduction: {(1 - after / before) * 100:.1f}%")


if __name__ == "__main__":
    shrink_geojson(
        input_path="ontario_road_network.geojson",
        output_path="ontario_roads_rounded.geojson",
        decimals=6,  # try 5 for more aggressive shrinking, see note above
    )
