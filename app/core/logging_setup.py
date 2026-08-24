from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
LOG_DIR=Path('logs'); LOG_DIR.mkdir(exist_ok=True)
def get_logger(name,account_id=None):
    logger=logging.getLogger(f'{name}:{account_id or "SYSTEM"}')
    if logger.handlers:return logger
    logger.setLevel(logging.INFO)
    fmt=logging.Formatter('%(asctime)s | %(levelname)s | %(message)s','%Y-%m-%d %H:%M:%S')
    for path in [LOG_DIR/'controller.log']+([LOG_DIR/f'account_{account_id}.log'] if account_id else []):
        h=RotatingFileHandler(path,maxBytes=5*1024*1024,backupCount=5,encoding='utf-8');h.setFormatter(fmt);logger.addHandler(h)
    logger.propagate=False;return logger
