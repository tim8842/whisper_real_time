def get_logging_dict_config():
    return {
        "version": 1,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "std": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "detailed"
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": "logs/main.log",
                "when": "d",
                "interval": 1,
                "backupCount": 30,
                "level": "DEBUG",
                "encoding": "UTF-8",
                "formatter": "detailed",
            }
        },
        "loggers": {
            "app": {
                "handlers": ["file"], # "handlers": ["std", "file"]
                "level": "DEBUG"
            }
        }
    }
