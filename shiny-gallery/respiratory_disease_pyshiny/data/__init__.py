from pandas import read_csv
from pathlib import Path

DATA_DIR = Path(__file__).parent.resolve()
# ASSET_DIR = APP_DIR.joinpath("assets").resolve()

polygon_data = read_csv(DATA_DIR.joinpath("countries.csv"))
polygon_data["coordinates"] = polygon_data["coordinates"].apply(eval)
points_from_polygons = read_csv(DATA_DIR.joinpath("points_from_polygons.csv"))

map_data_world_bank = (
    read_csv(DATA_DIR.joinpath("map_data_world_bank.csv"))
    .drop(["lng", "lat"], axis=1)
    .merge(points_from_polygons, on="Code")
)
map_data_oecd = (
    read_csv(DATA_DIR.joinpath("map_data_oecd.csv"))
    .drop(["lng", "lat"], axis=1)
    .merge(points_from_polygons, on="Code")
)

plot_data_world_bank = read_csv(DATA_DIR.joinpath("plot_data_world_bank.csv"))
plot_data_oecd = read_csv(DATA_DIR.joinpath("plot_data_oecd.csv"))
