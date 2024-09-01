from shiny import App, Inputs, Outputs, Session, ui
from pathlib import Path

from cpu_ux   import cpu_ui
from cpu_srvr import cpu_server

from rose import ASSET_DIR

from rose.log import setup_logging
setup_logging('app_cpu.log')

from rose.log import logger
logger.info("CPU App Start")

app_ui = ui.page_navbar(
    ui.head_content(
        ui.tags.meta(name="viewport", content="width=device-width, initial-scale=1"),
        ui.include_css(Path("assets")/"styles.css"),
    ),
    ui.nav_panel("Menu1", cpu_ui),
    ui.nav_spacer(), #---
    ui.nav_menu("Links",
        ui.nav_control(ui.a("onesixx", href="https://onesixx.com/", target="_blank")),
        "----",
        ui.nav_control(ui.a("shiny", href="https://shiny.posit.co/py/", target="_blank")),
        align="right",
    ),
    # ui.nav_control(ui.input_dark_mode(id="dark_mode", mode="light")),
    theme= ASSET_DIR.joinpath("my_theme.css"),
    title = ui.tags.img(src='imgs/apptitle.png', alt='App Title Image', style="height:2rem;"),
    id = "Menu1",
    selected = "log",
)
def server(input: Inputs, output: Outputs, session: Session):
    cpu_server(input, output, session)

app = App(app_ui, server, static_assets= ASSET_DIR)
