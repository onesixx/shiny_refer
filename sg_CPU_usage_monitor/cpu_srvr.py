from shiny import Inputs, Outputs, Session, reactive, render
from rose import DATA_DIR

from rose.log import logger
logger.info("c_server start")

import matplotlib
import numpy as np
import pandas as pd

from psutil import cpu_count, cpu_percent
from helpers import plot_cpu

def cpu_server(input, output, session):
    pass