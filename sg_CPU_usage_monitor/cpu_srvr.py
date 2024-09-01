from shiny import Inputs, Outputs, Session, reactive, render
from rose import DATA_DIR

from rose.log import logger
logger.info("c_server start")

def cpu_server(input, output, session):
    pass