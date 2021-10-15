import logging
import json


class JSONFormatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        log_output = {
            'ts': record.created,
            'app': record.module,
            'level': record.levelname,
            'logger_name': record.funcName,
            'message': record.msg
        }

        if record.__dict__['stack']:
            log_output['stack'] = repr(record.__dict__['stack'])

        record.msg = json.dumps(log_output)
        return super().format(record)


class Log:
    def __init__(self, level: str = 'DEBUG') -> None:
        self.level = level

        json_stream_handler = logging.StreamHandler()
        json_stream_handler.setFormatter(JSONFormatter())

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(json_stream_handler)
        self.logger.setLevel(self.level)

    def debug(self, message: str, stack: object = None) -> None:
        self.logger.debug(message, extra={'stack': stack}, stacklevel=2)

    def info(self, message: str, stack: object = None) -> None:
        self.logger.info(message, extra={'stack': stack}, stacklevel=2)

    def warning(self, message: str, stack: object = None) -> None:
        self.logger.warning(message, extra={'stack': stack}, stacklevel=2)

    def error(self, message: str, stack: object = None) -> None:
        self.logger.error(message, extra={'stack': stack}, stacklevel=2)
