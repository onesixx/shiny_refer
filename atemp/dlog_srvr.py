from shiny import ui, Inputs, Outputs, Session, reactive, render
from rose import DATA_DIR

import duckdb
from rose import DATA_DIR, BACKEND_DIR
import pandas as pd
from datetime import date, timedelta
import subprocess

from rose.log import logger
logger.info("dlog_server start")

from config import AREA_LIST

def fetch_extracted_dates():
    conn = duckdb.connect(str(DATA_DIR.joinpath("db/buda.db")), read_only=False)
    resultdf = conn.query("""
        SELECT * FROM daily
        WHERE saved = True
        ORDER BY date DESC;
    """).to_df()
    conn.close()
    extracted_dates = list(set(resultdf['date']))
    extracted_dates = [day.strftime('%Y-%m-%d') for day in extracted_dates]
    return extracted_dates

TODAY = date.today()
YESTERDAY = TODAY - timedelta(days=1)
WEEKAGO   = TODAY - timedelta(days=7)

def dlog_server(input, output, session):
    ###### ------ Sidebar ------ ######
    @output
    @render.ui
    def log_day_duration_UI():
        # extracted_dates = fetch_extracted_dates()
        # logger.info(f"extracted_dates : {extracted_dates}")
        # if input.navset_tab_id == 'Job Daily':
        return ui.input_date("job_day", "Select Date :",
            #max=YESTERDAY,
            value=YESTERDAY,
            # datesdisabled= extracted_dates
        )
        # elif input.navset_tab_id() == 'Remove data':
        #     return ui.input_date("job_day", "Select Date : ",
        #         max=YESTERDAY, value=YESTERDAY)

    @render.ui
    @reactive.event(input.log_swh_show)
    def log_switchUI():
        if not input.log_swh_show():
            return ui.TagList(
                ui.output_ui("log_day_duration_UI")
            )
        else:
            return ui.TagList(
                ui.input_date_range("job_dayrange", "Select Date :",
                    #max = YESTERDAY,
                    start=WEEKAGO,
                    end=YESTERDAY,
                ),
            )
    # ###### ------ Process ------ ######
    # @render.ui
    # @reactive.event(input.log_btn_fetch)
    # def hello():
    #     return ui.p(f"Hello", class_="fs-1 text-primary mt-3")


    @reactive.calc
    @reactive.event(input.log_btn_fetch)
    def bpro_loadData_all():
        logger.info(f"PRESS FETCH")
        if not input.log_swh_show():
            duration_date = [input.job_day().strftime('%Y%m%d')]
        else:
            duration_date = [day.strftime('%Y%m%d') for day in input.job_dayrange()]
        logger.info(f"duration_date : {duration_date}")

        with ui.Progress(min=1, max=100) as p:
            p.set(detail = "This may take a while...")
            alldata = {}
            for i, area in enumerate(AREA_LIST):
                for report in ['dt_compact', 'dt_detail']:
                    sheet = f"{area}_{report}"
                    p.set(10+2*i, message = f"Processing '{sheet}'...")
                    file_path = [ DATA_DIR.joinpath("process", f"{area}", f"{report}_{selected_date}.parquet") \
                        for selected_date in duration_date \
                        if DATA_DIR.joinpath("process", f"{area}", f"{report}_{selected_date}.parquet").exists() ]
                    df_parquet_temp = [ pd.read_parquet(file, engine='pyarrow') for file in file_path ]
                    if len(df_parquet_temp) > 0:
                        data_from_file = pd.concat(df_parquet_temp, ignore_index=True)
                        if not data_from_file.empty:
                            if report == 'dt_compact':
                                data_from_file.columns = [
                                    'area_id', 'date', 'machine_id',
                                    'load_cnt', 'duration',
                                    'assign', 'acquire', 'deposit'
                                ]
                            elif report == 'dt_detail':
                                data_from_file.columns = [
                                    'area_id', 'date', 'machine_id',
                                    'load_cnt', 'start_time', 'end_time', 'duration',
                                    'assign', 'acquire', 'deposit'
                                ]
                            alldata[sheet] = data_from_file
                            for key, df in alldata.items():
                                if 'date' in df.columns:
                                    alldata[key]['date'] = pd.to_datetime(alldata[key]['date'], format='%Y-%m-%d')
                        else:
                            alldata[sheet] = pd.DataFrame()
                    else:
                        alldata[sheet] = pd.DataFrame()
            return alldata


    @reactive.calc
    def bpro_loadData():
        alldata = bpro_loadData_all()
        logger.info(f"alldata : {alldata}")
        selected_area = input.log_sel_area()
        ### ------ dt_compact ------ ###
        df_dt_compact = alldata[selected_area+'_dt_compact'] \
            if selected_area+'_dt_compact' in alldata.keys() else pd.DataFrame()
        if df_dt_compact.empty:
            df_dt_compact = pd.DataFrame()
        else:
            if input.log_swh_show():
                ddf = df_dt_compact.copy()
                agg_dict = {
                    "date", "sum",
                }
                df_dt_compact = ddf.groupby('date').agg(agg_dict).round(2).reset_index()
        # logger.info(f"df_dt_compact : {df_dt_compact.shape}")

        ### ------ dt_detail ------ ###
        df_dt_detail = alldata[selected_area+'_dt_detail'] \
            if selected_area+'_dt_detail' in alldata.keys() else pd.DataFrame()
        if df_dt_detail.empty:
            df_dt_detail = pd.DataFrame()
        # logger.info(f"df_dt_detail : {df_dt_detail.shape}")

        return df_dt_compact, df_dt_detail


    @output
    @render.data_frame
    def bpro_tbl_dt_compact():
        df_dt_compact = bpro_loadData()[0]
        dff = df_dt_compact.copy()
        if dff.shape[0] > 0:
            if 'date' in dff.columns:
                #dff['date'] = dff['date'].dt.strftime('%Y-%m-%d')
                dff['date'] = dff['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
            if not input.log_swh_show():
                style=[
                    { "cols": [0,1,2], "class": "posit-blue-bg"},
                    { "cols": [3,4,5], "class": "posit-green-bg"},
                ]
            else:
                style=[
                    { "cols": [0,1,2], "class": "posit-blue-bg"},
                    { "cols": [3,4,5], "class": "posit-green-bg"},
                ]
            return render.DataGrid(dff,
                selection_mode="row",
                width="100%",
                filters=input.bpro_filter_dt_compact(),
                # style=style
            )

    @output
    @render.text
    def bpro_tbl_dt_compact_nodata_msg():
        df_dt_compact = bpro_loadData()[0]
        logger.info(f"df_dt_compact : {df_dt_compact.shape}")
        if df_dt_compact.empty or df_dt_compact is None:
            return "No data available"
        return ""


    # @render.ui
    # def bpro_tbl_ds_facility_rate():
    #     df_dt_compact = bpro_loadData()[1]
    #     if len(df_dt_compact) > 0:
    #         avg_row = df_dt_compact['assigned'].sum() / (df_dt_compact['assigned'].sum() + df_dt_compact['unassigned'].sum())
    #         avg_row = (avg_row * 100).round(2)
    #     else:
    #         avg_row = 0






            # return render.DataGrid(dff,
            #     selection_mode="row",
            #     width="100%",
            #     filters=input.bpro_ds_filter(),
            #     style=style
            # )
    ###### ------ JOB ------ ######
    @render.text
    @reactive.event(input.job_btn_jobdaily)
    def job_txt_job_result():
        if not input.log_swh_show():
            day = input.job_day()
            day_str = day.strftime('%Y%m%d')
            pgm = BACKEND_DIR.joinpath("daily.py")

            with ui.Progress(min=1, max=100) as p:
                p.set(detail = "This may take a while...")
                p.set(50, message = "Processing...")
                complete = subprocess.run(["python", str(pgm), "--from", day_str])
        else:
            day = input.job_dayrange()
            logger.info(f"day : {day}")
            day_from_str = day[0].strftime('%Y%m%d')
            day_to_str = day[1].strftime('%Y%m%d')
            day_str = f"{day_from_str} ~ {day_to_str}"
            pgm = BACKEND_DIR.joinpath("daily_batch.py")

            with ui.Progress(min=1, max=100) as p:
                p.set(detail = "This may take a while...")
                p.set(50, message = "Processing...")
                complete = subprocess.run(["python", str(pgm), "--from", day_from_str, "--to", day_to_str])

        if complete.returncode == 0:
            return f"Job Start : {day_str}"
        else:
            return f"Job Failed : {day_str}"

    @render.text
    @reactive.event(input.job_btn_removedaily)
    def job_txt_remove_result():
        if not input.log_swh_show():
            day = input.job_day()
            day_str = day.strftime('%Y%m%d')
            pgm = BACKEND_DIR.joinpath("daily_remove.py")
            with ui.Progress(min=1, max=100) as p:
                p.set(detail = "This may take a while...")
                p.set(50, message = "Processing...")
                complete = subprocess.run(["python", str(pgm), "--from", day_str])
        else:
            day = input.job_dayrange()
            day_from_str = day[0].strftime('%Y%m%d')
            day_to_str = day[1].strftime('%Y%m%d')
            day_str = f"{day_from_str} ~ {day_to_str}"
            pgm = BACKEND_DIR.joinpath("daily_remove_batch.py")
            with ui.Progress(min=1, max=100) as p:
                p.set(detail = "This may take a while...")
                p.set(50, message = "Processing...")
                complete = subprocess.run(["python", str(pgm), "--from", day_from_str, "--to", day_to_str])
        if complete.returncode == 0:
            return f"Remove Start : {day_str}"
        else:
            return f"Remove Failed : {day_str}"

    ###### ------ END ------ ######
