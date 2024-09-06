from shiny import ui
from rose import DATA_DIR
from assets.icons import *

from rose.log import logger
logger.info("dlog_ui start")

from config import AREA_LIST

dlog_ui = ui.layout_sidebar(
    ui.sidebar(
        ui.input_switch("log_swh_show", "Duration"),
        ui.output_ui("log_switchUI"),
        ###### ------ Process ------ ######
        ui.tags.hr(class_="mt-0"),
        ui.input_action_button("log_btn_fetch", "Fetch"),
        ui.input_select("log_sel_area", "Select Area :",
            choices= {k:k for k in AREA_LIST},
            selected= AREA_LIST[0],
        ),
        ## todo
        title="sidebar controls",
        class_="sidebar",
        open="desktop"
    ),
    ui.navset_tab(
        ###### ------ Process ------ ######
        ui.nav_panel("Process",
            ui.layout_columns(
                ui.value_box("AAA", ui.output_ui("bpro_tbl_AAA"), showcase=dollar),
                ui.value_box("BBB", ui.output_ui("bpro_tbl_BBB"), showcase=biztime),
                ui.value_box("CCC", ui.output_ui("bpro_tbl_CCC"), showcase=wrench),
                col_widths=[4, 4, 4],
                fill=False,
                title="overview"
            ),
            ui.card(
                ui.card_header(
                    ui.span(f"summary   ",
                            ui.input_action_link("bpro_info_dt_compact", "", icon=info_fill, class_="float-right")
                    ),
                    ui.input_switch('bpro_filter_dt_compact', 'Filter', False),
                    class_= "d-flex justify-content-between"
                ),
                ui.output_data_frame("bpro_tbl_dt_compact"),
                ui.output_text("bpro_tbl_dt_compact_nodata_msg")
            ),
            #ui.output_ui("bpro_ui_dt_detail"),
        ),
        ###### ------ JOB ------ ######
        ui.nav_panel("Job Daily",
            ui.markdown("""
                press the button to start the job & remove the job
            """),
            ### Do JOB
            ui.tooltip(
                ui.input_task_button("job_btn_jobdaily", "Job Start",  class_="mt-4"),
                "Start the job",
            ),
            ui.tags.br(),
            ui.output_text_verbatim("job_txt_job_result"),

            ### Remove JOB
            ui.input_task_button("job_btn_removedaily", "Remove", class_="mt-4"),
            ui.tags.br(),
            ui.output_text_verbatim("job_txt_remove_result"),
        ),

        id = 'navset_tab_id'
    ),
)