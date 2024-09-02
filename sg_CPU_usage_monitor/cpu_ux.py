from shiny import ui
from rose import DATA_DIR

from rose.log import logger
logger.info("c_ui start")

cpu_sidebar = ui.sidebar(
        ui.input_select(
            "cmap",
            "Colormap",
            {
                "inferno": "inferno",
                "viridis": "viridis",
                "copper": "copper",
                "prism": "prism (not recommended)",
            },
        ),
        ui.input_action_button("reset", "Clear history", class_="btn-sm"),
        ui.input_switch("hold", "Freeze output", value=False),
        title="sidebar controls",
        class_= "sidebar",
        open="desktop"
    )

cpu_main = ui.navset_tab(
    ui.nav_panel("Graphs",
        ui.input_numeric("sample_count", "Number of samples per graph", 50),
        ui.output_plot('plot'),
    ),
    ui.nav_panel("Heatmap",
        ui.input_numeric("table_rows", "Rows to display", 15),
        ui.output_table('table'),
    ),
    #title="CPU %",
    #class_="main",
    #open="desktop"
)

cpu_ui = ui.page_bootstrap(
    ui.page_sidebar(
        cpu_sidebar,
        cpu_main,
        class_="wrapper",
    )
)