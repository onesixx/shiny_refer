from shiny import ui
from rose import DATA_DIR

from rose.log import logger
logger.info("database_ui start")

from rose.mod_query import mod_query_ui
import os

db_folder = DATA_DIR.joinpath("db")
db_list = [f for f in os.listdir(db_folder) if os.path.isfile(os.path.join(db_folder, f)) and f.endswith('.db')]
db_list_no_ext = [os.path.splitext(f)[0] for f in db_list]

init_ex_sql = """
SELECT * from information_schema.columns
"""
# SELECT * from "penguins.csv" limit 5
# SELECT * from daily limit 10

db_ui = ui.page_sidebar(
    ui.sidebar(
        # ui.output_ui("db_ui_sel_catalog"),
        ui.input_select("db_sel_catalog", "Select Database",
            #choices={"job.db":"job", "csv.db":"csv"},
            choices={k:v for k,v in zip(db_list, db_list_no_ext)},
            selected="job.db"),
        ui.input_action_button("db_btn_addQuery", "Add Query", class_="btn btn-primary"),
        # ui.output_text("db_txt_currentdb"),
    ),
    ui.navset_tab(
        ui.nav_panel("Query",
            ui.tags.div(
                mod_query_ui("query_0_job", remove_id="query_0_job", qry=init_ex_sql),
                id="module_container", class_="mt-3"
            ),
        ),
        ui.nav_panel("Table",
            ui.card(
                ui.card_header("Table Info."),
                ui.output_data_frame("db_df_tableinfo"),
                class_="mt-3 d-table",
            ),
            ui.output_ui("db_rui_columninfo"),
        ),
        ui.nav_panel("Catalog",
            ui.row(
                ui.layout_column_wrap(
                    ui.card(
                        ui.card_header("Create DB", class_='bg-light'),
                        ui.input_text("db_txt_createdb", "New DB (Catalog):", placeholder="input new catalog name"),
                        ui.input_action_button("db_btn_createdb", "Create DB", class_="btn btn-warning"),
                        ui.output_text("db_txt_createdbresult"),
                    ),
                    ui.card(
                        ui.card_header("Create table from csv file", class_='bg-light'),
                        ui.input_file("db_file_csv", "Upload csv file ", accept=[".csv"], multiple=False),
                        ui.output_text("db_txt_csvResult"),
                        ui.markdown(
                            """
                            The table created from csv file will be in 'csv' catalog.
                            """
                        ),
                    ),
                ),
                class_="mt-3"
            ),
        ),
        selected="Query"
    )
    # class_="bslib-page-dashboard",
)
