import logging 
import sys
from datetime import datetime

logger = logging.getLogger("CloudCostOptimizer")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    fmt  = '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

def get_logger(name):
    return logging.getLogger(f"CloudCostOptimizer.{name}")