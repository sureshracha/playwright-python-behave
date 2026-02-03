
# logger_utils.py
import logging
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

import test_context as context


@dataclass
class LoggerOptions:
    file_name: str
    logfile_folder: str


class LocalTimeFormatter(logging.Formatter):
    """
    Produces lines similar to:
    [<local datetime>] : level: message

    TS used:
      format.printf(info => `[${new Date().toLocaleString()}] : ${info.level}: ${info.message}`)
    """
    def format(self, record: logging.LogRecord) -> str:
        local_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname.lower()
        message = record.getMessage()
        return f"[{local_ts}] : {level}: {message}"


def options(logger_options: LoggerOptions) -> dict:
    """
    TS returned Winston 'options' object. In Python we return a dict describing config.
    (You can use configure_logger() below to apply it.)
    """
    log_path = Path(logger_options.logfile_folder) / f"{logger_options.file_name}.log"
    return {
        "log_file": str(log_path),
        "level": logging.INFO,
        "formatter": LocalTimeFormatter(),
    }


def configure_logger(logger_options: LoggerOptions, logger_name: str = "test") -> logging.Logger:
    """
    Creates/configures a logger to write to <logfileFolder>/<file_name>.log.
    Equivalent to Winston File transport with level 'info'.
    """
    cfg = options(logger_options)

    # Ensure folder exists
    Path(logger_options.logfile_folder).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(logger_name)
    logger.setLevel(cfg["level"])
    logger.propagate = False  # avoid duplicate logs if root logger has handlers

    # Prevent adding multiple handlers if configure_logger called repeatedly
    if not any(isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", "") == cfg["log_file"]
               for h in logger.handlers):
        file_handler = logging.FileHandler(cfg["log_file"], mode="a", encoding="utf-8")
        file_handler.setLevel(cfg["level"])
        file_handler.setFormatter(cfg["formatter"])
        logger.addHandler(file_handler)

    # Attach to shared context (mimics context.testContext.logger)
    context.testContext = context.TestContext(logger=logger)
    return logger


def info(msg: str) -> None:
    """
    TS:
      context.testContext.logger.info(msg);
      if (!msg.toLowerCase().includes('password')) console.log(msg);
    """
    if context.testContext is None or context.testContext.logger is None:
        raise RuntimeError("testContext.logger is not configured. Call configure_logger() first.")

    context.testContext.logger.info(msg)
    if "password" not in msg.lower():
        print(msg)


def error(msg: str) -> None:
    """
    TS:
      context.testContext.logger.error(msg);
      console.log(msg);
    """
    if context.testContext is None or context.testContext.logger is None:
        raise RuntimeError("testContext.logger is not configured. Call configure_logger() first.")

    context.testContext.logger.error(msg)
    print(msg)


# ---- Optional: async wrappers (only for API parity) ----
async def info_async(msg: str) -> None:
    info(msg)

async def error_async(msg: str) -> None:
    error(msg)
 
