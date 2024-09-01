from shiny import App, Inputs, Outputs, Session, ui
from pathlib import Path

from a_ux import a_ui
from a_srvr import a_server

from basic_ux import bas_ui
from basic_srvr import bas_server

from c_ux import my_ui
from c_srvr import my_server

from dlog_ux import dlog_ui
from dlog_srvr import dlog_server

from database_ux import db_ui
from database_srvr import db_server

from rose.log import logger
logger.info("App Start")
from rose import ASSET_DIR

app_ui = ui.page_navbar(
    ui.head_content(
        ui.tags.meta(name="viewport", content="width=device-width, initial-scale=1"),
        ui.include_css(Path("assets")/"styles.css"),
    ),
    ui.nav_panel("Menu1", a_ui),
    ui.nav_panel("Menu2", bas_ui),
    ui.nav_panel("Menu3", my_ui),
    ui.nav_panel("log", dlog_ui),
    ui.nav_panel("Database", db_ui),
    ui.nav_spacer(), #---
    ui.nav_menu("Links",
        ui.nav_control(ui.a("onesixx", href="https://onesixx.com/", target="_blank")),
        "----",
        ui.nav_control(ui.a("shiny", href="https://shiny.posit.co/py/", target="_blank")),
        align="right",
    ),
    ui.nav_control(ui.input_dark_mode(id="dark_mode", mode="light")),
    theme= ASSET_DIR.joinpath("my_theme.css"),
    title = ui.tags.img(src='imgs/apptitle.png', alt='App Title Image', style="height:2rem;"),
    id = "menus",
    selected = "log",
)
def server(input: Inputs, output: Outputs, session: Session):
    a_server(input, output, session)
    bas_server(input, output, session)
    my_server(input, output, session)
    db_server(input, output, session)
    #dlog_ui(input, output, session)

app = App(app_ui, server, static_assets= ASSET_DIR)
