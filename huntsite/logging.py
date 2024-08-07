import inspect
import logging
import sys
import time
import uuid

from django.conf import settings
import django.utils.log
from logtail import LogtailHandler
from loguru import logger
import sentry_sdk.integrations.logging

LOCAL_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
    "| <level>{level: <8}</level> "
    "| <yellow>{extra[request_id]}</yellow> "
    "| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
    "- <level>{message}</level>"
)
PRODUCTION_FORMAT = "{extra[request_id]} | {name}:{function}:{line} - {message}"

logger.remove(0)
if settings.DEPLOY_ENVIRONMENT == settings.ENVIRONMENT_ENUM.LOCAL:
    # Console logger
    logger.add(sys.stderr, format=LOCAL_FORMAT, backtrace=True, diagnose=True)
elif settings.DEPLOY_ENVIRONMENT == settings.ENVIRONMENT_ENUM.PRODUCTION:
    # Console logger
    logger.add(sys.stderr, format=PRODUCTION_FORMAT, backtrace=True, diagnose=True)
    # Logtail logger
    if settings.LOGTAIL_SOURCE_TOKEN:
        logtail_handler = LogtailHandler(source_token=settings.LOGTAIL_SOURCE_TOKEN)
        logger.add(logtail_handler, format=PRODUCTION_FORMAT, backtrace=False, diagnose=False)
elif settings.DEPLOY_ENVIRONMENT == settings.ENVIRONMENT_ENUM.TEST:
    # No logging
    pass

# Skip these logging module files when finding the caller of a log message
# https://github.com/getsentry/sentry-python/issues/2982#issuecomment-2270465880
LOGGING_LIBRARY_MODULE_FILES = {
    logging.__file__,
    django.utils.log.__file__,
    sentry_sdk.integrations.logging.__file__,
    __file__,
}


# InterceptHandler
# https://github.com/Delgan/loguru?tab=readme-ov-file#entirely-compatible-with-standard-logging
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename in LOGGING_LIBRARY_MODULE_FILES):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).bind(request_id="N/A").log(
            level, record.getMessage()
        )


# https://betterstack.com/community/guides/logging/loguru/#creating-a-request-logging-middleware
def logging_middleware(get_response):
    def middleware(request):
        # Create a request ID
        request_id = str(uuid.uuid4())

        # Add context to all loggers in all views
        with logger.contextualize(request_id=request_id):
            start_time = time.perf_counter()
            response = get_response(request)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # After the response is received
            logger.info(
                "{method} '{path}' {status_code} ({elapsed_ms:.0f} ms)",
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                elapsed_ms=elapsed_ms,
            )

            response["X-Request-ID"] = request_id

            return response

    return middleware
