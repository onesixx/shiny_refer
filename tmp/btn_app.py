import matplotlib.pyplot as plt
import numpy as np
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from rose.log import setup_logging
from rose.log import logger

setup_logging('app.log')
logger.info("btn Start")

app_ui = ui.page_fluid(
    ui.input_slider("n", "zzz",
        0, 1000,500,
    ),
    ui.input_action_button("go", "Go!", class_="btn-success"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    @reactive.event(input.go, ignore_none=False)
    def plot():
        logger.info("aaaaaaaaa")
        return None


app = App(app_ui, server)
