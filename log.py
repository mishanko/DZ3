import logging


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename="./logs/app.log",
    filemode="a",
    datefmt='%d-%b-%y %H:%M:%S'
)

log = logging.getLogger(__name__)
