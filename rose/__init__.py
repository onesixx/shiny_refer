from rose.log import setup_logging
setup_logging('atemp_app.log')

from rose.log import logger
logger.info("Let's go, rose!!")

from .config import (
    HOME_DIR,
    DOWNLOADS_DIR,

    BASE_DIR,
    ASSET_DIR,
    BACKEND_DIR,
    DATA_DIR,
    DOC_DIR,
    TMP_DIR,

    ASSET_DIR_R,
)
