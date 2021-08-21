from .log import logger # Must be imported before .app!
from .app import app
import uvicorn

if __name__ == "__main__":
    logger.info("Starting staticker")
    uvicorn.run(app, host='0.0.0.0')
