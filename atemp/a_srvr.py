from shiny import Inputs, Outputs, Session, reactive, render, req
import pandas as pd
from vega_datasets import data

from rose import DATA_DIR
from rose.mod_plot_scatter import mod_plot_scatter_server
from rose.log import logger
logger.info("c_server start")

def a_server(input: Inputs, output: Outputs, session: Session):
    g_marker_data = reactive.value([])
    def gather_marker_data(marker_data):
        logger.info(f"marker_data - app: {marker_data}")
        g_marker_data.set(marker_data)

    @reactive.calc
    @reactive.event(input.button)
    def plotdata() -> pd.DataFrame:
        cars = data.cars()
        # cylinders_order = sorted(cars['Cylinders'].unique())
        # cat_type = CategoricalDtype(categories=cylinders_order, ordered=True)
        # cars['Cylinders'] = cars['Cylinders'].astype(cat_type)
        cars['Cylinders'] = cars['Cylinders'].astype('object')  # Cylinders 열의 데이터 타입을 object로 변경
        return cars

    @reactive.effect
    def _() -> None:
        req(plotdata() is not None)
        mod_plot_scatter_server("example_plot", df=plotdata(),
            x_selected='Horsepower',
            y_selected='Miles_per_Gallon',
            label_selected='Origin',
            label_excluded=['Name'],
            title = "My Title",
            height =500,
            _on_click=gather_marker_data)