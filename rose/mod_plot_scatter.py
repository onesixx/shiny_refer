"""
Shiny module for plotting scatter plots.
"""
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from shiny import ui, Inputs, Outputs, Session, render, reactive, module, req
from shiny.plotutils import near_points, brushed_points
from htmltools import HTML
from faicons import icon_svg

from rose.log import logger
from rose.utils import tooltip_style, show_modal_warning
from assets.icons import triangle_fill, square_fill, x_lg

### ------ Set seaborn context and style ------
sns.set_context('paper') # notebook, paper, poster : Setting the scale of font/line/marker elements
sns.set_palette(sns.color_palette("colorblind")) # Set1, Set2, Set3, Paired, color_palette() ...
sns.set_style("whitegrid")

@module.ui
def mod_plot_scatter_ui():
    return ui.output_ui("draw_plot_in_ui")

@module.server
def mod_plot_scatter_server(input: Inputs, output: Outputs, session: Session,
    df: pd.DataFrame,
    x_axis=None, x_selected=None, x_excluded=[],
    y_axis=None, y_selected=None, y_excluded=[],
    label_vars=None, label_selected=None, label_excluded=[],
    title = "Scatter plot",
    height = 666,
    _on_click =[]) -> str:

    ### ------ Prepare all Data & Axis & Label ------
    plotdata = df.copy()
    x_axis     = x_axis or [col for col in plotdata.columns.tolist() if col not in x_excluded]
    x_selected = x_selected or x_axis[0]
    y_axis     = y_axis or [col for col in plotdata.columns.tolist() if col not in y_excluded]
    y_selected = y_selected or y_axis[1]
    label_vars         = label_vars or [col for col in plotdata.select_dtypes(exclude="number").columns if col not in label_excluded]
    label_selected = label_selected or label_vars[0]

    @render.ui
    @reactive.event(input.sel_l)
    def label_vals():
        # if input.facet():
        #     ui.remove_ui("[id$='chkgrp_labels']")
        # else:
        return ui.input_checkbox_group("chkgrp_labels", "",
            choices  = {str(value): ui.span(str(value)) for value in plotdata[input.sel_l()].unique()},
            selected = [str(value) for value in plotdata[input.sel_l()].unique()],
            inline   = True
        )

    ### ------ Plot UX ------
    @output
    @render.ui
    def draw_plot_in_ui() -> ui.Tag:
        return ui.card(
            ui.card_header(
                ui.span(f"{title}"),
                ui.div(
                    ui.input_action_button("btn_heightPlus", '',icon=icon_svg("plus"),
                        style="padding: .2rem .3rem .2rem .5rem; margin-right: .6rem;"),
                    ui.input_action_button("btn_heightMinus",'',icon=icon_svg("minus"),
                        style="padding: .2rem .3rem .2rem .5rem;")
                ),
                style="display:flex; justify-content: space-between;"
            ),
            ui.card_body(
                ui.layout_sidebar(
                    ### ------ Plot Control UX ------
                    ui.sidebar(
                        ui.markdown("Control"),
                        ui.accordion(
                            ui.accordion_panel("Axis",
                                ui.input_select("sel_x", "X-axis",
                                    choices=x_axis, selected=x_selected),
                                ui.input_select("sel_y", "Y-axis",
                                    choices=y_axis, selected=y_selected),
                                ui.input_select("sel_l", "label",
                                    choices=label_vars, selected=label_selected),
                                ui.output_ui('label_vals')
                            ),
                            ui.accordion_panel("facet",
                                ui.input_switch("facet", "facet", False),
                            ),
                            ui.accordion_panel("Marker",
                                # https://matplotlib.org/stable/api/markers_api.html#module-matplotlib.markers
                                ui.layout_column_wrap( # default:circle "o" "^" "s" "x"
                                    ui.input_action_button("classA",  "ClassA",  icon=triangle_fill, style="font-size:.66rem; padding:.2rem .3rem .2rem .5rem;"),
                                    ui.input_action_button("classB",  "ClassB",  icon=square_fill,   style="font-size:.66rem; padding:.2rem .3rem .2rem .5rem;"),
                                    ui.input_action_button("outlier", "Outlier", icon=x_lg,          style="font-size:.66rem; padding:.2rem .3rem .2rem .5rem;"),
                                    width=1/3
                                ),
                                ui.layout_column_wrap(
                                    ui.input_action_button("marker_remove",    "Remove", icon=icon_svg("eraser"),      style="font-size:.88rem; padding:.2rem .3rem .2rem .5rem;"),
                                    ui.input_action_button("marker_reset_all", "Reset",  icon=icon_svg("rotate-left"), style="font-size:.88rem; padding:.2rem .3rem .2rem .5rem;"),
                                    width=1/2
                                )
                            ),
                            multiple=False,
                        ),
                        position = 'right',
                        open = 'open', #'closed',
                        bg = "#f8f8f8",
                    ),
                    ### ------ Plot Area UX *** ------
                    ui.output_ui("mainplot_ui"),
                )
            ),
            class_="mt-3",
            full_screen=True
        )

    rct_plot_height = reactive.value(height)
    rct_lable_cnt = reactive.value(0)
    @output
    @render.ui
    def mainplot_ui() -> ui.Tag:
        plot_height = rct_plot_height.get()
        return   ui.row(
            ui.output_plot("mainplot",
                height=plot_height, width='100%',
                ### ------ Mouse action ------
                # hover_opts_kwargs = {}
                # brush_opts_kwargs = {}
                click   =ui.click_opts(),
                hover   =ui.hover_opts(), #**hover_opts_kwargs),
                brush   =ui.brush_opts(), #**brush_opts_kwargs),
                dblclick=ui.dblclick_opts(),
            ),
            ui.output_ui("tooltip"),
        )

    ### ------ mainplot ------
    rct_marker_idx = reactive.value([[], [], []])
    @output
    @render.plot(alt="Matplotlib scatterplot")
    def mainplot():
        req(not plotdata.empty)

        ### ------ session.resetBrush() -------
        ui.remove_ui("[id$='mainplot_brush']")

        ### ------ Label & Color  ------
        label_values = plotdata[input.sel_l()].unique()
        palette = sns.color_palette("hls", len(label_values))
        colors = {label: palette[i] for i, label in enumerate(label_values)}

        ### ------ Facet ------
        rct_lable_cnt.set(len(label_values))
        nrows = len(label_values) if input.facet() else 1

        if np.issubdtype(plotdata[input.sel_x()].dtype, np.number):
            x_min = plotdata[input.sel_x()].min()
            x_max = plotdata[input.sel_x()].max()
            is_numeric_x = True
        else:
            x_unique_values = sorted(plotdata[input.sel_x()].astype(str).unique())
            is_numeric_x = False

        if np.issubdtype(plotdata[input.sel_y()].dtype, np.number):
            y_min = plotdata[input.sel_y()].min()
            y_max = plotdata[input.sel_y()].max()
            is_numeric_y = True
        else:
            is_numeric_y = False


        ### ------ Marker ------
        marker_data = rct_marker_idx.get()
        #logger.info(f"marker_data - module :{marker_data}")

        ### ------ create a figure ------
        fig, axes = plt.subplots(nrows=nrows, ncols=1, figsize=(8, nrows * 4))

        for i, selected_label in enumerate(label_values):
            ax = axes[i] if nrows > 1 else axes  # for facet
            plotdata_filtered_label = plotdata[plotdata[input.sel_l()] == selected_label]

            ### --- Label transparency ---
            alpha_value = 1 if str(selected_label) in input.chkgrp_labels() else 0.06

            ### ------ mainplot ------
            ax.scatter(
                x= plotdata_filtered_label[input.sel_x()],
                y= plotdata_filtered_label[input.sel_y()],
                label=str(selected_label),
                marker='.',
                facecolors='none', edgecolors=colors[selected_label],  # Set border-color for markers
                alpha=alpha_value
            )
            ax.legend()
            ### ------ for beauty ------
            ax.grid(True, linestyle='--', linewidth=0.6, alpha=0.5)
            ax.spines[["left", "top", "right"]].set_visible(False) # remove border
            ax.tick_params(axis='y', length=0) # Remove y-axis ticks

            ### ------ brush & double click to zoom -------
            if rct_x_zoom_ranges.get() != [None, None] or rct_y_zoom_ranges.get() != [None, None]:
                ax.set_xlim(rct_x_zoom_ranges.get())
                ax.set_ylim(rct_y_zoom_ranges.get())
            else:
                ### ------ fix axis ------
                if is_numeric_x:
                    ax.set_xlim(x_min*.8 , x_max*1.04)  # for beauty
                else:
                    ax.margins(x=0.05)  # for beauty
                    ax.set_xticklabels(x_unique_values, rotation=45, ha='right')
                if is_numeric_y:
                    ax.set_ylim(y_min*.8 , y_max*1.04)  # for beauty
                else:
                    ax.margins(y=0.05)  # for beauty

            ### ------ set Labels ------
            if (nrows+1)//2 -1 == i:    # for middle row
                ax.set_ylabel(input.sel_y().replace('_', ' '), fontweight='bold', fontsize='large')
            ax.set_xlabel(input.sel_x().replace('_', ' '), fontweight='bold', fontsize='large')

        ### ------ Marker : Overpaint brushed data with marker ------
        if any(len(inner_list) > 0 for inner_list in marker_data):

            for i, selected_label in enumerate(label_values):
                ax = axes[i] if nrows > 1 else axes  # for facet
                plotdata_filtered_label = plotdata[plotdata[input.sel_l()] == selected_label]
                for j, marker_list in enumerate(marker_data):
                    marker = ['^', 's', 'x'][j]
                    if marker_list:
                        valid_indices = [idx for idx in marker_list if idx in plotdata_filtered_label.index]
                        x_values = [plotdata_filtered_label[input.sel_x()][idx] for idx in valid_indices]
                        y_values = [plotdata_filtered_label[input.sel_y()][idx] for idx in valid_indices]
                        if x_values and y_values:
                            ax.scatter(
                                x=x_values,
                                y=y_values,
                                marker=marker,
                                color = 'black',
                                alpha=.5  # for beauty
                            )

        return fig

    ### ------ brush & double click to zoom ------
    rct_x_zoom_ranges = reactive.value([None, None])
    rct_y_zoom_ranges = reactive.value([None, None])

    @reactive.effect
    @reactive.event(input.mainplot_dblclick)
    def _zoom_brushed_area_with_dblclick():
        brushed_info = input.mainplot_brush()
        # logger.info(f'brushed_info : {brushed_info}')
        if brushed_info is not None:
            rct_x_zoom_ranges.set([brushed_info['xmin'], brushed_info['xmax']])
            rct_y_zoom_ranges.set([brushed_info['ymin'], brushed_info['ymax']])
        else:
            ### ------ reset zoom ------
            rct_x_zoom_ranges.set([None, None])
            rct_y_zoom_ranges.set([None, None])

    ### ------ hover & Tooltip ------
    @output
    @render.ui()
    @reactive.event(input.mainplot_hover)
    def tooltip():
        hover_info     = input.mainplot_hover()
        selected_xaxis = input.sel_x()
        selected_yaxis = input.sel_y()
        # logger.info(f'hover_info : {hover_info}')

        click_near_pnts_df = near_points(
            plotdata,
            coordinfo = hover_info,
            xvar = selected_xaxis,
            yvar = selected_yaxis,
            threshold=6,
            add_dist=True,
            max_points=1,
            all_rows=False
        )
        req(not click_near_pnts_df.empty)
        # logger.info(f'click_near_pnts : \n {click_near_pnts_df}')
        tooltip_text = f"""
            <b>{selected_xaxis}:</b> {click_near_pnts_df[selected_xaxis].iloc[0]}<br>
            <b>{selected_yaxis}:</b> {click_near_pnts_df[selected_yaxis].iloc[0]}<br>
            <b>{input.sel_l()}:</b> {click_near_pnts_df[input.sel_l()].iloc[0]}
        """
        return ui.panel_well(
            HTML(tooltip_text),
            id="tooltip",
            style = tooltip_style(hover_info, offset_left=-15, offset_top=15)
        )

    ### marker data control
    def get_brushed_points():
        brushed_df = brushed_points(
            plotdata,
            brush = input.mainplot_brush(),
            xvar = input.sel_x(),
            yvar = input.sel_y(),
        )
        # logging.info(f"get_brushed_points:{brushed_df}")
        return brushed_df

    def update_marker_data(new_marker_list, update_type):
        old_marker_data = rct_marker_idx.get()
        old_marker_data_A = set(old_marker_data[0])
        old_marker_data_B = set(old_marker_data[1])
        old_marker_data_X = set(old_marker_data[2])

        marker_data = [[], [], []]

        if update_type == 'classA':
            marker_data[0] = list(old_marker_data_A.union(set(new_marker_list)))
            if old_marker_data_B:
                marker_data[1] = list(old_marker_data_B.difference(set(new_marker_list)))
            if old_marker_data_X:
                marker_data[2] = list(old_marker_data_X.difference(set(new_marker_list)))
        elif update_type == 'classB':
            marker_data[1] = list(old_marker_data_B.union(set(new_marker_list)))
            if old_marker_data_A:
                marker_data[0] = list(old_marker_data_A.difference(set(new_marker_list)))
            if old_marker_data_X:
                marker_data[2] = list(old_marker_data_X.difference(set(new_marker_list)))
        elif update_type == 'outlier':
            marker_data[2] = list(old_marker_data_X.union(set(new_marker_list)))
            if old_marker_data_A:
                marker_data[0] = list(old_marker_data_A.difference(set(new_marker_list)))
            if old_marker_data_B:
                marker_data[1] = list(old_marker_data_B.difference(set(new_marker_list)))
        elif update_type == 'remove':
            if old_marker_data_A:
                marker_data[0] = list(old_marker_data_A.difference(set(new_marker_list)))
            if old_marker_data_B:
                marker_data[1] = list(old_marker_data_B.difference(set(new_marker_list)))
            if old_marker_data_X:
                marker_data[2] = list(old_marker_data_X.difference(set(new_marker_list)))
        ### ------ update new marker data ------
        rct_marker_idx.set(marker_data)
        # logger.info(f"update_marker_data:{marker_data}")
        return marker_data

    @reactive.effect
    @reactive.event(input.classA)
    def classA_brushed():
        brushed_df = get_brushed_points()
        if brushed_df.empty:
            show_modal_warning("Brush first on data",
                title="Warning : There is no brushed data ")
        else:
            new_marker_list = brushed_df.index.to_list()
            marker_data = update_marker_data(new_marker_list, 'classA')
            _on_click(rct_marker_idx.get())

    @reactive.effect
    @reactive.event(input.classB)
    def classB_brushed():
        brushed_df = get_brushed_points()
        if brushed_df.empty:
            show_modal_warning("Brush first on data",
                title="Warning : There is no brushed data ")
        else:
            new_marker_list = brushed_df.index.to_list()
            marker_data = update_marker_data(new_marker_list, 'classB')
            _on_click(rct_marker_idx.get())

    @reactive.effect
    @reactive.event(input.outlier)
    def outlier_brushed():
        brushed_df = get_brushed_points()
        if brushed_df.empty:
            show_modal_warning("Brush first on data",
                title="Warning : There is no brushed data ")
        else:
            new_marker_list = brushed_df.index.to_list()
            marker_data = update_marker_data(new_marker_list, 'outlier')
            _on_click(rct_marker_idx.get())

    @reactive.effect
    @reactive.event(input.marker_remove)
    def _reset_remove():
        brushed_df = get_brushed_points()
        if brushed_df.empty:
            show_modal_warning("Brush first on data",
                title="Warning : There is no brushed data ")
        else:
            new_marker_list = brushed_df.index.to_list()
            marker_data = update_marker_data(new_marker_list,  'remove')
            _on_click(rct_marker_idx.get())

    @reactive.effect
    @reactive.event(input.marker_reset_all)
    def _reset_all():
        logging.info("reset_all")
        rct_marker_idx.set([[], [], []])
        _on_click(rct_marker_idx.get())


    ### ------ Prepare Plot size plus/minus------
    @reactive.effect
    @reactive.event(input.btn_heightPlus)
    def _():
        if rct_plot_height.get() >= 400:
            rct_plot_height.set(rct_plot_height.get() + 100)

    @reactive.effect
    @reactive.event(input.btn_heightMinus)
    def _():
        if rct_plot_height.get() >= 500:
            rct_plot_height.set(rct_plot_height.get() - 100)

    ### ------ Detail hegiht :: Initialize a flag to track the first run ------
    facet_initialized = reactive.value(False)
    @reactive.effect
    @reactive.event(input.facet)
    def _():
        if not facet_initialized.get():
            facet_initialized.set(True)
            return  # Skip the first run
        if rct_lable_cnt.get() != 0 :
            # logger.info(f"rct_plot_height.get() : {rct_plot_height.get()} ")
            if input.facet():
                rct_plot_height.set(rct_plot_height.get() * rct_lable_cnt.get() *0.6 )
            else:
                rct_plot_height.set(rct_plot_height.get() / rct_lable_cnt.get() *1.6666667)
