
# test_context.py
import logging
from dataclasses import dataclass
from typing import Optional


@dataclass
class TestContext:
    logger: logging.Logger


# This mimics: context.testContext.logger
testContext: Optional[TestContext] = None
