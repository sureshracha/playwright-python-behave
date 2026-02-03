
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

import test_context as context
import logger_utils as logger  # rename to your actual logger module (e.g., import logger)


def _norm_string(val: Any, case_sensitive: bool) -> Any:
    """
    TS behavior:
      if typeof actual/expected === 'string', trim and optionally lowercase
    Python:
      if it's a str, strip and optionally lower
    """
    if isinstance(val, str):
        val = val.strip()
        return val if case_sensitive else val.lower()
    return val


def _ensure_soft_list() -> List[Dict[str, Any]]:
    """
    Ensures context.testContext.assertsJson.soft exists and is a list.
    """
    if context.testContext is None:
        raise RuntimeError("testContext is not configured.")

    if not hasattr(context.testContext, "assertsJson") or context.testContext.assertsJson is None:
        # Create a minimal structure if missing
        context.testContext.assertsJson = {}

    if isinstance(context.testContext.assertsJson, dict):
        context.testContext.assertsJson.setdefault("soft", [])
        soft = context.testContext.assertsJson["soft"]
    else:
        # If assertsJson is an object with attribute 'soft'
        if not hasattr(context.testContext.assertsJson, "soft"):
            context.testContext.assertsJson.soft = []
        soft = context.testContext.assertsJson.soft

    if not isinstance(soft, list):
        # Reset if corrupted
        soft = []
        if isinstance(context.testContext.assertsJson, dict):
            context.testContext.assertsJson["soft"] = soft
        else:
            context.testContext.assertsJson.soft = soft

    return soft


# -----------------------------
# Soft assertions
# -----------------------------

def soft_assert(actual: Any, expected: Any, message: str, case_sensitive: bool = False) -> None:
    if isinstance(actual, str) and isinstance(expected, str):
        actual_n = _norm_string(actual, case_sensitive)
        expected_n = _norm_string(expected, case_sensitive)
    else:
        actual_n, expected_n = actual, expected

    if actual_n == expected_n:
        logger.info(f"softAssert :: {message} {{Actual : [{actual_n}] - Expected [{expected_n}]}}")
    else:
        logger.error(f"softAssert :: {message} {{Actual : [{actual_n}] - Expected [{expected_n}]}}")
        soft = _ensure_soft_list()
        soft.append({
            "softAssert": "Failed",
            "caseSensitive": str(case_sensitive),
            "Actual": str(actual_n),
            "Expected": str(expected_n),
            "message": str(message),
        })


def soft_contains(actual: Any, expected: Any, message: str, case_sensitive: bool = False) -> None:
    if isinstance(actual, str) and isinstance(expected, str):
        actual_n = _norm_string(actual, case_sensitive)
        expected_n = _norm_string(expected, case_sensitive)
    else:
        actual_n, expected_n = actual, expected

    # TS expects .includes, so treat as string operation where possible
    if str(expected_n) in str(actual_n):
        logger.info(f"softContains :: {message} {{String : [{actual_n}] - Substring [{expected_n}]}}")
    else:
        logger.error(f"softContains :: {message} {{String : [{actual_n}] - Substring [{expected_n}]}}")
        soft = _ensure_soft_list()
        soft.append({
            "softContains": "Failed",
            "caseSensitive": str(case_sensitive),
            "Actual": str(actual_n),
            "Expected": str(expected_n),
            "message": str(message),
        })


def soft_not_contains(actual: Any, expected: Any, message: str, case_sensitive: bool = False) -> None:
    actual_n = _norm_string(actual, case_sensitive)
    expected_n = _norm_string(expected, case_sensitive)

    if str(expected_n) not in str(actual_n):
        logger.info(f"softNotContains :: {message} {{String : [{actual_n}] - Substring [{expected_n}]}}")
    else:
        logger.error(f"softNotContains :: {message} {{String : [{actual_n}] - Substring [{expected_n}]}}")
        soft = _ensure_soft_list()
        soft.append({
            "softNotContains": "Failed",
            "caseSensitive": str(case_sensitive),
            "Actual": str(actual_n),
            "Expected": str(expected_n),
            "message": str(message),
        })


def soft_contains_for_string_array(
    actual: List[str],
    expected: Any,
    message: str,
    case_sensitive: bool = False
) -> None:
    """
    TS:
      actual = caseSensitive ? actual : actual.toString().toLowerCase().split(',')
      expected = caseSensitive ? expected.trim() : expected.toLowerCase().trim()
      if (actual.indexOf(expected) >= 0) pass else fail
    """
    if case_sensitive:
        actual_list = actual
        expected_n = str(expected).strip()
    else:
        actual_list = ",".join(actual).lower().split(",")
        actual_list = [x.strip() for x in actual_list if x is not None]
        expected_n = str(expected).lower().strip()

    if expected_n in actual_list:
        logger.info(f"softContainsForStringArray :: {message} {{Array : [{actual_list}] - Element [{expected_n}]}}")
    else:
        logger.error(f"softContainsForStringArray :: {message} {{Array : [{actual_list}] - Element [{expected_n}]}}")
        soft = _ensure_soft_list()
        soft.append({
            "softContainsForStringArray": "Failed",
            "caseSensitive": str(case_sensitive),
            "Actual": str(actual_list),
            "Expected": str(expected_n),
            "message": str(message),
        })


def soft_not_contains_for_string_array(
    actual: List[str],
    expected: Any,
    message: str,
    case_sensitive: bool = False
) -> None:
    if case_sensitive:
        actual_list = actual
        expected_n = str(expected).strip()
    else:
        actual_list = ",".join(actual).lower().split(",")
        actual_list = [x.strip() for x in actual_list if x is not None]
        expected_n = str(expected).lower().strip()

    if expected_n not in actual_list:
        logger.info(f"softNotContainsForStringArray :: {message} {{Array : [{actual_list}] - Element [{expected_n}]}}")
    else:
        logger.error(f"softNotContainsForStringArray :: {message} {{Array : [{actual_list}] - Element [{expected_n}]}}")
        soft = _ensure_soft_list()
        soft.append({
            "softNotContainsForStringArray": "Failed",
            "caseSensitive": str(case_sensitive),
            "Actual": str(actual_list),
            "Expected": str(expected_n),
            "message": str(message),
        })


def soft_assert_compare_string_arrays(
    actual: List[str],
    expected: List[str],
    message: str,
    case_sensitive: bool = False
) -> None:
    """
    TS:
      diffVals = actual.filter(item => expected.indexOf(item) < 0);
      flag = (diffVals.length === 0);
    Note: TS code ignores caseSensitive here; we keep same behavior by default.
    If you want case-insensitive comparison, I can add it.
    """
    diff_vals = [item for item in actual if item not in expected]
    flag = (len(diff_vals) == 0)

    if flag:
        logger.info(f"softAssertCompareArrays :: {message} {{Actual : [{actual}] - Expected  [{expected}]}}")
    else:
        logger.error(f"softAssertCompareArrays :: {message} {{Actual : [{actual}] - Expected  [{expected}]}}")
        soft = _ensure_soft_list()
        soft.append({
            "softAssertCompareArrays": "Failed",
            "caseSensitive": str(case_sensitive),
            "Actual": str(actual),
            "Expected": str(expected),
            "message": str(message),
            "differnce": f"[{diff_vals}]",
        })


def soft_contains_one_of_them(
    actual: Any,
    expected: List[str],
    message: str,
    case_sensitive: bool = False
) -> None:
    actual_n = _norm_string(actual, case_sensitive)

    if case_sensitive:
        expected_list = expected
    else:
        expected_list = ",".join(expected).lower().split(",")
        expected_list = [e.strip() for e in expected_list]

    flag = any(e.strip() in str(actual_n) for e in expected_list if e is not None)

    if flag:
        logger.info(f"softContainsOneOfThem :: {message} {{Actual : [{actual_n}] - Expected One of Them [{expected_list}]}}")
    else:
        logger.error(f"softContainsOneOfThem :: {message} {{Actual : [{actual_n}] - Expected One of Them [{expected_list}]}}")
        soft = _ensure_soft_list()
        soft.append({
            "softContainsOneOfThem": "Failed",
            "caseSensitive": str(case_sensitive),
            "Actual": str(actual_n),
            "ExpectedOneofThem": str(expected_list),
            "message": str(message),
        })


def soft_not_contains_one_of_them(
    actual: Any,
    expected: List[str],
    message: str,
    case_sensitive: bool = False
) -> None:
    actual_n = _norm_string(actual, case_sensitive)

    if case_sensitive:
        expected_list = expected
    else:
        expected_list = ",".join(expected).lower().split(",")
        expected_list = [e.strip() for e in expected_list]

    flag = any(e.strip() in str(actual_n) for e in expected_list if e is not None)

    if flag:
        logger.error(f"softNotContainsOneOfThem :: {message} {{Actual : [{actual_n}] - Expected One of Them [{expected_list}]}}")
        soft = _ensure_soft_list()
        soft.append({
            "softNotContainsOneOfThem": "Failed",
            "caseSensitive": str(case_sensitive),
            "Actual": str(actual_n),
            "ExpectedOneofThem": str(expected_list),
            "message": str(message),
        })
    else:
        logger.info(f"softNotContainsOneOfThem :: {message} {{Actual : [{actual_n}] - Expected One of Them [{expected_list}]}}")


# -----------------------------
# Hard assertions
# -----------------------------

def hard_assert(actual: Any, expected: Any, message: str) -> None:
    if actual == expected:
        logger.info(f"hardAssert :: {message} {{Actual : [{actual}] - Expected [{expected}]}}")
    else:
        logger.error(f"hardAssert :: {message} {{Actual : [{actual}] - Expected [{expected}]}}")
        raise AssertionError(f"hardAssert :: {message} {{Actual : [{actual}] - Expected [{expected}]}}")


def hard_contains(actual: str, expected: str, message: str) -> None:
    if expected in actual:
        logger.info(f"hardContains :: {message} {{Actual : [{actual}] - Expected [{expected}]}}")
    else:
        logger.error(f"hardContains :: {message} {{Actual : [{actual}] - Expected [{expected}]}}")
        raise AssertionError(f"hardContains :: {message} {{Actual : [{actual}] - Expected [{expected}]}}")


def hard_not_contains(actual: str, expected: str, message: str) -> None:
    if expected not in actual:
        logger.info(f"hardNotContains :: {message} {{String : [{actual}] - Substring [{expected}]}}")
    else:
        logger.error(f"hardNotContains :: {message} {{String : [{actual}] - Substring [{expected}]}}")
        raise AssertionError(f"hardNotContains :: {message}\n{{Actual : [{actual}] - Expected [{expected}]}}")
