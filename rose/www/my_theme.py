from pathlib import Path
from shiny import ui
from rose import ASSET_DIR
my_theme = (
    ui.Theme("sandstone")
    # "shiny", "bootstrap",
    # "cerulean", "cosmo", "flatly", "sandstone",
    # "journal", "litera", "lumen", "lux", "materia", "minty",
    # "morph", "pulse", "quartz",  "simplex",
    # "sketchy", "slate", "solar", "spacelab", "superhero",
    # "united", "vapor", "yeti", "zephyr".
    # "cyborg", "darkly",
    .add_defaults(
        my_purple="#aa00aa",
    )
    .add_mixins(
        headings_color="$my-purple",
    )
)

with open(ASSET_DIR / "my_theme.css", "w") as f:
    f.write(my_theme.to_css())