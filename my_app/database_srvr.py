from shiny import Inputs, Outputs, Session, reactive, render, ui, req
from rose import DATA_DIR
from rose.mod_query import mod_query_server, mod_query_ui

from rose.log import logger
logger.info("database_server start")
import duckdb
from shiny.types import FileInfo
import os
import pandas as pd


def db_server(input, output, session):
    ###### ------ Query --------------------------------------------------------
    mod_counter = reactive.value(0)
    mod_query_server("query_0_job", DATA_DIR.joinpath("db", "job.db") , remove_id="query_0_job")

    @reactive.effect
    @reactive.event(input.db_btn_addQuery)
    def _():
        # counter
        selected_db_file = input.db_sel_catalog()
        db_name = os.path.splitext(selected_db_file)[0]
        db_filepath = DATA_DIR.joinpath("db", selected_db_file)

        counter = mod_counter.get() + 1
        mod_counter.set(counter)
        id = "query_" + str(counter) + "_" + db_name
        # ui
        ui.insert_ui(
            selector="#module_container",
            where="afterBegin",
            ui=mod_query_ui(id, remove_id=id),
        )
        # server
        mod_query_server(id, db_filepath, remove_id=id)

    ###### ------ Table --------------------------------------------------------
    @reactive.calc
    def table_info() -> pd.DataFrame:
        query = """
        SELECT table_catalog, table_schema, table_name, table_type, is_insertable_into, is_typed, TABLE_COMMENT
        from information_schema.tables
        """
        # -- self_referencing_column_name, reference_generation, user_defined_type_catalog, user_defined_type_name, commit_action
        selected_db = input.db_sel_catalog()
        conn = duckdb.connect(str(DATA_DIR.joinpath("db", selected_db)), read_only=False)
        df = conn.execute(query).fetchdf()
        conn.close()
        return df

    @reactive.calc
    def column_info() -> pd.DataFrame:
        query = """
        SELECT table_name, ordinal_position, column_name, is_nullable, data_type, COLUMN_COMMENT
        from information_schema.columns
        """
        # -- table_catalog, table_schema
        # -- column_default, character_maximum_length, character_octet_length, numeric_precision, numeric_precision_radix, numeric_scale, datetime_precision, interval_type, interval_precision, character_set_schema, character_set_name, collation_schema, collation_name, domain_schema, domain_name, udt_catalog, udt_schema, udt_name, scope_catalog, scope_schema, scope_name, maximum_cardinality, dtd_identifier, is_self_referencing, is_identity, identity_generation, identity_start, identity_increment, identity_maximum, identity_minimum, identity_cycle, is_generated, generation_expression, is_updatable
        selected_db = input.db_sel_catalog()
        conn = duckdb.connect(str(DATA_DIR.joinpath("db", selected_db)), read_only=True)
        df = conn.execute(query).fetchdf()
        conn.close()
        return df

    @render.data_frame
    def db_df_tableinfo():
        return render.DataGrid(table_info(),
            summary=True, #"table {start} ~ {end} Total {total}",
            # height="200px",
            selection_mode='rows'
        )

    @output
    @render.data_frame
    def db_df_selectedtable():
        data_selected = db_df_tableinfo.data_view(selected=True)
        req(not data_selected.empty)
        table_name = data_selected["table_name"].values[0]
        df = column_info()
        df = df[df["table_name"]==table_name]
        return render.DataGrid(df)

    @render.ui
    def db_rui_columninfo():
        return ui.card(
            ui.card_header("Column Info."),
            ui.output_data_frame("db_df_selectedtable"),
            class_="mt-3 d-table",
        )


    ###### ------ Catalog --------------------------------------------------------
    @reactive.calc
    @reactive.event(input.db_btn_createdb)
    def create_db():
        req(input.db_txt_createdb().strip() !="")
        newdb_nm = input.db_txt_createdb() + ".db"
        conn = duckdb.connect(str(DATA_DIR.joinpath("db", newdb_nm)), read_only=False)
        conn.close()
        logger.info(f"New Database Created: {newdb_nm}")
        return f"New Database Created : {newdb_nm}"

    @output
    @render.text
    def db_txt_createdbresult():
        result = create_db()
        logger.info(f"db_txt_createdbresult: {result}")
        req(result is not None)
        return result

    @reactive.calc
    def parse_file():
        file: list[FileInfo] | None = input.db_file_csv()
        req(file is not None, "Please upload a file")

        with ui.Progress(min=1, max=100) as _p:
            _p.set(message="Progressing...", detail="This may take a while...")
            _p.set(30, message="file uploading...")
            csv_nm = os.path.splitext(file[0]["name"])[0] # dict_keys(['name', 'size', 'type', 'datapath'])
            csv_datapath = file[0]["datapath"]
            # db_file_nm = csv_nm(".",0)+".db"
            # db_file = DATA_DIR.joinpath("db", db_file_nm)
            _p.set(60, message="file uploaded successfully!")
            db_file = DATA_DIR.joinpath("db", "csv.db")
            conn = duckdb.connect(str(db_file), read_only=False)
            conn.execute(f"""
                CREATE TABLE '{csv_nm}' AS SELECT * FROM read_csv_auto('{csv_datapath}')
            """)
            # table = table.replace("NA", np.nan)
            conn.close()
            _p.set(100, message="Done Processing!")
        return "Done Processing!"

    @output
    @render.text
    def db_txt_csvResult():
        result = parse_file()
        logger.info(f"db_txt_csvResult: {result}")
        req(result is not None)
        return result
