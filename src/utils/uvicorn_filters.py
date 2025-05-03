import logging
from typing import override


class HealthCheckFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord):
        return record.getMessage().find("GET /healthz") == -1
