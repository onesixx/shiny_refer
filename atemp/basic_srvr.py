from shiny import Inputs, Outputs, Session, reactive, render
from rose import DATA_DIR

import pandas as pd
import seaborn as sns

from rose.log import logger
logger.info("server start")

from rose.utils import show_modal_warning

def bas_server(input: Inputs, output: Outputs, session: Session):
    df = pd.read_csv(DATA_DIR.joinpath("penguins.csv"))

    @reactive.calc
    def filtered_df():
        filt_df = df[df["species"].isin(input.bas_chk_species())]
        filt_df = filt_df.loc[filt_df["body_mass_g"] < input.bas_sld_mass()]
        return filt_df

    @render.text
    def bas_txt_count():
        return filtered_df().shape[0]

    @render.text
    def bas_txt_billLength():
        return f"{filtered_df()['bill_length_mm'].mean():.1f} mm"

    @render.text
    def bas_txt_billDepth():
        return f"{filtered_df()['bill_depth_mm'].mean():.1f} mm"

    @render.plot
    def bas_plt_lengthDepth():
        return sns.scatterplot(
            data=filtered_df(),
            x="bill_length_mm",
            y="bill_depth_mm",
            hue="species",
        )

    @render.data_frame
    def bas_df_summaryStats():
        cols = [
            "species",
            "island",
            "bill_length_mm",
            "bill_depth_mm",
            "body_mass_g",
        ]
        return render.DataGrid(filtered_df()[cols], filters=True)

    from shiny import ui
    def show_modal_html(msg, title="info", style=""):
        msg_mod_not_selected = ui.modal(
            ui.div(
                ui.HTML(msg),
                style=style,
            ),
            title=title,
            size="xl",
            easy_close=True,
            footer=None,
        )
        ui.modal_show(msg_mod_not_selected)

    @reactive.effect
    @reactive.event(input.bas_btn_info)
    def _():
        logger.info("Button clicked")
        msg = """
            <ul>
                <li>following a successful audition in 2012</li>
                <li> and trained for four years </li>
                <li> before debuting as a member</li>
                <li> of the South Korean girl group Blackpink </li>
                <li>following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012</li>
                <li> and trained for four years </li>
                <li> before debuting as a member</li>
                <li> of the South Korean girl group Blackpink </li>
                <li>following a successful audition in 2012</li>
                <li> and trained for four years </li>
                <li> before debuting as a member</li>
                <li> of the South Korean girl group Blackpink </li>
                <li>following a successful audition in 2012</li>
                <li> and trained for four years </li>
                <li> before debuting as a member</li>
                <li> of the South Korean girl group Blackpink </li>
                <li>following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012</li>
                <li> and trained for four years </li>
                <li> before debuting as a member</li>
                <li> of the South Korean girl group Blackpink </li>
                <li>following a successful audition in 2012</li>
                <li> and trained for four years </li>
                <li> before debuting as a member</li>
                <li> of the South Korean girl group Blackpink </li>
                <li>following a successful audition in 2012</li>
                <li> and trained for four years </li>
                <li> before debuting as a member</li>
                <li> of the South Korean girl group Blackpink </li>
                <li>following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012</li>
                <li> and trained for four years </li>
                <li> before debuting as a member</li>
                <li> of the South Korean girl group Blackpink </li>
                <li>following a successful audition in 2012</li>
                <li> and trained for four years </li>
                <li> before debuting as a member</li>
                <li> of the South Korean girl group Blackpink </li>
                <li>following a successful audition in 2012</li>
                <li> and trained for four years </li>
                <li> before debuting as a member</li>
                <li> of the South Korean girl group Blackpink </li>
                <li>following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012following a successful audition in 2012</li>
                <li> and trained for four years </li>
                <li> before debuting as a member</li>
                <li> of the South Korean girl group Blackpink </li>
                <li>following a successful audition in 2012</li>
                <li> and trained for four years </li>
                <li> before debuting as a member</li>
                <li> of the South Korean girl group Blackpink </li>
            </ul>
            """
        show_modal_html(msg, "table info", style="color: blue;")
