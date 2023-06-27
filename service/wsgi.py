from app import application, logger, started_info
from waitress import serve

if __name__ == "__main__":
    logger.debug("logger was initialized")
    logger.debug(started_info)
    serve(application, host="0.0.0.0", port=5000, threads=4)