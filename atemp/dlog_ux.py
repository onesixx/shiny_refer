from shiny import ui
from rose import DATA_DIR

from rose.log import logger
logger.info("dlog_ui start")

dlog_ui = ui.layout_sidebar(
    ui.sidebar(
        ## todo
        title="sidebar controls",
    ),
    ui.layout_columns(
        ui.card(
            full_screen=True,
        ),
        ui.card(
            full_screen=True,
        ),
    )
)