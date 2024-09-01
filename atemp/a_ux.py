from shiny import ui
from faicons import icon_svg

from rose import DATA_DIR
from rose.mod_plot_scatter import mod_plot_scatter_ui, mod_plot_scatter_server

from rose.log import logger
logger.info("c_ui start")

a_ui = ui.layout_sidebar(
    ui.sidebar(
        ## todo
        ui.input_action_button("button", label="Draw Plot",
            icon=icon_svg("chart-simple")),
        ui.br(),
        title="sidebar controls",
    ),
    mod_plot_scatter_ui("example_plot"),
    ui.layout_columns(
        ui.card(
            full_screen=True,
        ),

    )
)