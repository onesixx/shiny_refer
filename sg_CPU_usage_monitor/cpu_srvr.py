from shiny import Inputs, Outputs, Session, reactive, render
from rose import DATA_DIR

from rose.log import logger
logger.info("c_server start")

import matplotlib
import numpy as np
import pandas as pd

from psutil import cpu_count, cpu_percent
from helpers import plot_cpu

# The agg matplotlib backend seems to be a little more efficient than the default when
# running on macOS, and also gives more consistent results across operating systems
matplotlib.use("agg")
# max number of samples to retain
MAX_SAMPLES = 1000
# secs between samples
SAMPLE_PERIOD = 1
ncpu = cpu_count(logical=True)

def cpu_server(input, output, session):
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


    @render.plot
    def plot():
        return plot_cpu(
            cpu_history_with_hold(), input.sample_count(), ncpu, input.cmap()
        )

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