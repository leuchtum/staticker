from uvicorn.config import LOGGING_CONFIG
import logging

log_config = LOGGING_CONFIG
log_config["loggers"]["testlogger"] = {"handlers": ["default"], "level": "DEBUG"}
logging.config.dictConfig(log_config)

logger = logging.getLogger("testlogger")
