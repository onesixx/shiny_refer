# This app is translated from Mastering Shinywidgets
# https://mastering-shiny.org/basic-reactivity.html#reactive-expressions-1
from shiny import App, render, ui
from numpy import random

# Functions we import from stats.py
from stats import freqpoly, t_test

app_ui = ui.page_fluid(
    ui.row(
        ui.column(
            4,
            "Distribution 1",
            ui.input_numeric("n1", label="n", value=1000, min=1),
            ui.input_numeric("mean1", label="Mean", value=0, step=0.1),
            ui.input_numeric("sd1", label="Sd", value=0.5, min=0.1, step=0.1),
        ),
        ui.column(
            4,
            "Distribution 2",
            ui.input_numeric("n2", label="n", value=1000, min=1),
            ui.input_numeric("mean2", label="Mean", value=0, step=0.1),
            ui.input_numeric("sd2", label="Sd", value=0.5, min=0.1, step=0.1),
        ),
        ui.column(
            4,
            "Frequency polygon",
            ui.input_numeric("binwidth", label="Bin width", value=0.1, step=0.1),
            ui.input_slider("range", label="range", value=[-3, 3], min=-5, max=5),
        ),
    ),
    ui.row(
        ui.column(9, ui.output_plot("hist")),
        ui.column(3, ui.output_text_verbatim("ttest")),
    ),
)


def server(input, output, session):
    @output
    @render.plot
    def hist():
        print(input.range())
        x1 = random.normal(input.mean1(), input.sd1(), input.n1())
        x2 = random.normal(input.mean2(), input.sd2(), input.n2())
        return freqpoly(x1, x2, input.binwidth(), input.range())

    @output
    @render.text
    def ttest():
        x1 = random.normal(0, 1, 100)
        x2 = random.normal(0, 1, 100)
        return t_test(x1, x2)


app = App(app_ui, server)
