# import sys
# if "pyodide" in sys.modules:
#     # psutil doesn't work on pyodide--use fake data instead
#     from fakepsutil import cpu_count, cpu_percent
# else:
#     from psutil import cpu_count, cpu_percent

import sys
# psutil: 시스템 및 프로세스 유틸리티 라이브러리
#        시스템 정보(CPU, 메모리, 디스크, 네트워크 등)를 제공하는 Python 모듈
# pyodide: 웹 브라우저에서 Python 코드를 실행할 수 있게 해주는 프로젝트
#        이는 WebAssembly를 사용하여 Python 인터프리터를 브라우저에서 실행할 수 있게 합니다.
# psutil은 pyodide환경에서 작동하지 않습니다.
# 이는 psutil이 시스템 호출을 사용하여 시스템 정보를 수집하는데,
# 브라우저 환경에서는 이러한 시스템 호출이 지원되지 않기 때문에 pyodide 환경에서는
# psutil 대신 fakepsutil이라는 모듈을 사용하여 가짜 데이터를 사용합니다.

if "pyodide" in sys.modules:
    from fakepsutil import cpu_count, cpu_percent
else:
    from psutil import cpu_count, cpu_percent


import matplotlib
import numpy as np
import pandas as pd
from helpers import plot_cpu

from shiny import reactive
from shiny.express import input, output, render, ui

# The agg matplotlib backend seems to be a little more efficient than the default when
# running on macOS, and also gives more consistent results across operating systems
matplotlib.use("agg")

# max number of samples to retain
MAX_SAMPLES = 1000
# secs between samples
SAMPLE_PERIOD = 1

ncpu = cpu_count(logical=True)

ui.page_opts(fillable=True)


@reactive.calc
def cpu_current():
    reactive.invalidate_later(SAMPLE_PERIOD)
    return cpu_percent(percpu=True)


cpu_history = reactive.value(None)


@reactive.calc
def cpu_history_with_hold():
    # If "hold" is on, grab an isolated snapshot of cpu_history; if not, then do a
    # regular read
    if not input.hold():
        return cpu_history()
    else:
        # Even if frozen, we still want to respond to input.reset()
        input.reset()
        with reactive.isolate():
            return cpu_history()


@reactive.effect
def collect_cpu_samples():
    """cpu_percent() reports just the current CPU usage sample; this Effect gathers
    them up and stores them in the cpu_history reactive value, in a numpy 2D array
    (rows are CPUs, columns are time)."""

    new_data = np.vstack(cpu_current())
    with reactive.isolate():
        if cpu_history() is None:
            cpu_history.set(new_data)
        else:
            combined_data = np.hstack([cpu_history(), new_data])
            # Throw away extra data so we don't consume unbounded amounts of memory
            if combined_data.shape[1] > MAX_SAMPLES:
                combined_data = combined_data[:, -MAX_SAMPLES:]
            cpu_history.set(combined_data)


@reactive.effect(priority=100)
@reactive.event(input.reset)
def reset_history():
    cpu_history.set(None)


ui.tags.style(
    """
    /* Don't apply fade effect, it's constantly recalculating */
    .recalculating {
        opacity: 1;
    }
    """
)

# Disable busy indicators
ui.busy_indicators.use(spinners=False, pulse=False)

with ui.sidebar():
    ui.input_select(
        "cmap",
        "Colormap",
        {
            "inferno": "inferno",
            "viridis": "viridis",
            "copper": "copper",
            "prism": "prism (not recommended)",
        },
    )
    ui.input_action_button("reset", "Clear history", class_="btn-sm")
    ui.input_switch("hold", "Freeze output", value=False)

with ui.card():
    with ui.navset_bar(title="CPU %"):
        with ui.nav_panel(title="Graphs"):
            ui.input_numeric("sample_count", "Number of samples per graph", 50)

            @render.plot
            def plot():
                return plot_cpu(
                    cpu_history_with_hold(), input.sample_count(), ncpu, input.cmap()
                )

        with ui.nav_panel(title="Heatmap"):
            ui.input_numeric("table_rows", "Rows to display", 15)

            @output(suspend_when_hidden=False)
            @render.table
            def table():
                history = cpu_history_with_hold()
                latest = pd.DataFrame(history).transpose().tail(input.table_rows())
                if latest.shape[0] == 0:
                    return latest
                return (
                    latest.style.format(precision=0)
                    .hide(axis="index")
                    .set_table_attributes(
                        'class="dataframe shiny-table table table-borderless font-monospace"'
                    )
                    .background_gradient(cmap=input.cmap(), vmin=0, vmax=100)
                )
