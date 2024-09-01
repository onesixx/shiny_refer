import duckdb
from shiny import module, reactive, render, ui
from faicons import icon_svg
# import pandas as pd

# example_query = """
# INSERT INTO daily (date, name, saved)
# VALUES ('2024-06-04', 'Daily', TRUE)
# ON CONFLICT (date, name)
# DO UPDATE SET saved = excluded.saved;
# """
META_SQL = """
SELECT * from information_schema.columns
"""

@module.ui
def mod_query_ui(remove_id, qry=META_SQL):
    return (
        ui.card( {"id":remove_id},
            ui.card_header(
                ui.span(f"{remove_id}"),
                ui.input_action_link("btn_rmv", "", class_="btn-close"),
                class_="cardheader-btn",
                #class_="d-flex justify-content-between align-items-center",
            ),
            ui.layout_columns(
                [
                    ui.input_text_area("sql_query", "",
                        value=qry,
                        width="100%", height="200px",
                    ),
                    ui.layout_columns(
                        ui.input_action_button("btn_execute", "Execute", icon=icon_svg("play"), class_="btn btn-primary"),
                    ),
                ],
                ui.output_table("results"),
                col_widths={"xl":[4,8], "lg":[4, 8], "md":[6, 6], "sm":[12, 12]},
            ),
        ),
    )

@module.server
def mod_query_server(input, output, session,
    db_file, remove_id):
    @render.table
    @reactive.event(input.btn_execute)
    def results():
        conn = duckdb.connect(str(db_file), read_only=False)
        qry = input.sql_query().replace("\n", " ")
        df = conn.execute(qry).fetchdf()
        conn.close()
        return(
                df.style.set_table_attributes(
                    'class="dataframe shiny-table table w-auto"'
                )
                .hide(axis="index")
            )

    @reactive.effect
    @reactive.event(input.btn_rmv)
    def _():
        ui.remove_ui(selector=f"div#{remove_id}")
