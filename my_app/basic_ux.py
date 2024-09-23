from shiny import ui
from faicons import icon_svg

from rose.log import logger
logger.info("ui start")
from assets.icons import info_fill

bas_ui = ui.layout_sidebar(
    ui.sidebar(
        ui.input_slider("bas_sld_mass", "Mass", 2000, 6000, 6000),
        ui.input_checkbox_group("bas_chk_species", "Species",
            ["Adelie", "Gentoo", "Chinstrap"],
            selected=["Adelie", "Gentoo", "Chinstrap"],
        ),
        title="Filter controls",
    ),
    ui.layout_column_wrap(
        ui.value_box("Number of penguins",
            ui.output_text("bas_txt_count"),
            showcase=icon_svg("earlybirds"),
        ),
        ui.value_box("Average bill length",
            ui.output_text("bas_txt_billLength"),
            showcase=icon_svg("ruler-horizontal"),
        ),
        ui.value_box("Average bill depth",
            ui.output_text("bas_txt_billDepth"),
            showcase=icon_svg("ruler-vertical"),
        ),
        fill=False,
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header(
                "Bill length and depth ",
                ui.tooltip(info_fill,
                    "This plot shows the bill length and depth of penguins."),
            ),
            ui.output_plot("bas_plt_lengthDepth"),
            full_screen=True,
        ),
        ui.card(
            ui.card_header(
                "Penguin data  ",
                ui.input_action_link("bas_btn_info", "", icon=info_fill),
            ),
            ui.output_data_frame("bas_df_summaryStats"),
            full_screen=True,
        ),
    )
)