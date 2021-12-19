from .log import logger  # Must be imported before .app!
from .app import app
import uvicorn

DEBUG = True

if DEBUG:
    HOST = "127.0.0.1"
    PORT = 8000
else:
    HOST = "0.0.0.0"
    PORT = 80

if __name__ == "__main__":
    logger.info("Starting staticker")
    uvicorn.run(app, host=HOST, port=PORT)
