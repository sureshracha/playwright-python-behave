
from __future__ import annotations
from typing import Any, List


def convert_any_to_string(val: Any) -> str:
    """
    TS: return val.toString();
    Python: str(val)
    """
    return str(val)


def replace_all(val: str, replace_char: str) -> str:
    """
    TS logic:
      - if val is a String and contains replaceChar:
          remove all occurrences by split/join
      - else return val

    Python:
      - if it's a string: use str.replace to remove all occurrences
      - otherwise return original value (but signature implies string)
    """
    if isinstance(val, str) and replace_char in val:
        return val.replace(replace_char, "")
    return val


def get_index(source_array: List[List[str]], expected_values: List[str], exact_match: bool = False) -> int:
    """
    TS: findIndex row where for every expected value, some element in the row matches.

    exact_match = True:
      ele.trim().toLowerCase() == col_data.trim().toLowerCase()

    exact_match = False:
      ele.trim().toLowerCase().includes(col_data.trim().toLowerCase())

    Returns row index or -1.
    """
    expected_norm = [v.strip().lower() for v in expected_values]

    for row_idx, row in enumerate(source_array):
        # normalize row items safely
        row_norm = [(c or "").strip().lower() for c in row]

        ok = True
        for col_data in expected_norm:
            if exact_match:
                if col_data not in row_norm:
                    ok = False
                    break
            else:
                if not any(col_data in cell for cell in row_norm):
                    ok = False
                    break

        if ok:
            return row_idx

    return -1


def to_title_case(s: str) -> str:
    """
    TS:
      splits by space and title-cases each word using:
      word[0].toUpperCase() + word.substr(1).toLowerCase()

    Python equivalent:
      - preserves multiple spaces similarly? (TS collapses because split(' ') gives empty words too)
      We'll mirror common expected behavior: split on whitespace and join with single spaces.
    """
    words = s.split()
    return " ".join((w[:1].upper() + w[1:].lower()) if w else "" for w in words)


def to_camel_case(s: str) -> str:
    """
    TS uses regex:
      str.replace(/(?:^\\w|[A-Z]|\\b\\w|\\s+)/g, function(match, index) {...})

    Effectively:
      - remove whitespace
      - lowercase first token's first letter
      - uppercase subsequent word starts
      - keep existing letters; but typical outcome is lowerCamelCase.

    Python approach:
      - split on whitespace
      - lowercase first word fully
      - capitalize subsequent words (first letter uppercase, rest lowercase)
      NOTE: This is a practical approximation of the TS regex behavior.
    """
    parts = s.split()
    if not parts:
        return ""
    first = parts[0].lower()
    rest = [p[:1].upper() + p[1:].lower() if p else "" for p in parts[1:]]
    return first + "".join(rest)


 

# rpint(convert_any_to_string(123))              # "123"
# print(replace_all("a-b-c", "-"))               # "abc"

# arr = [["John", "Doe"], ["Jane", "Smith"], ["Foo bar", "Baz"]]
# print(get_index(arr, ["jane", "smi"], False))  # 1 (contains match)
# print(get_index(arr, ["Jane", "Smith"], True)) # 1 (exact match)

# print(to_title_case("hELLo wORLD"))            # "Hello World"
# print(to_camel_case("hello world test"))       # "helloWorldTest"
