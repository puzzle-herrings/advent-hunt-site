import inspect
import logging
import time
import uuid

import django.utils.log
from loguru import logger
import sentry_sdk.integrations.logging

# Skip these logging module files when finding the caller of a log message
# https://github.com/getsentry/sentry-python/issues/2982#issuecomment-2270465880
LOGGING_LIBRARY_MODULE_FILES = {
    logging.__file__,
    django.utils.log.__file__,
    sentry_sdk.integrations.logging.__file__,
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

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


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
            logger.bind(
                path=request.path,
                method=request.method,
                status_code=response.status_code,
                elapsed_ms=elapsed_ms,
            ).info(
                "{method} '{path}' {status_code} ({elapsed_ms} ms)",
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                elapsed_ms=f"{elapsed_ms:.0f}",
            )

            response["X-Request-ID"] = request_id

            return response

    return middleware
