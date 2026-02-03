from playwright.sync_api import Page, Locator
from typing import List, Optional, Any

class Base_Page:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, url: str):
        self.page.goto(url, timeout=60000)

    def drag_and_drop(self, source_selector, target_selector):
        try:
            self.page.drag_and_drop(source_selector, target_selector)
        except Exception as e:
            print(f"Error during drag and drop: {e}")
    
    def select_dropdown_option(self, selector: str, option: str, by: str = "value"):
        try:
            dropdown = self.page.locator(selector)
            if by == "value":
                dropdown.select_option(value=option)
            elif by == "label":
                dropdown.select_option(label=option)
            elif by == "index":
                dropdown.select_option(index=int(option))
            else:
                raise ValueError("Invalid 'by' parameter. Use 'value', 'label', or 'index'.")
        except Exception as e:
            print(f"Error selecting dropdown option '{option}' by '{by}': {e}")
    def get_text_all_matching_objects(self ) :
        """Return trimmed innerText for all elements matching the locator."""
        arr: List[str] = []
        count =   self.page.count()  # number of matched elements [1](https://playwright.dev/python/docs/api/class-locator)
        for i in range(count):
            text = self.page.nth(i).inner_text()  # [1](https://playwright.dev/python/docs/api/class-locator)
            arr.append(text.strip())
        return arr

    def get_css(self,  css_value: str) -> str:
        """
        Returns computed CSS property value for the first matched element.
        Similar behavior to your TS: returns 'Invalid property' if empty.
        """
        # Evaluate in browser context with the element as first argument [1](https://playwright.dev/python/docs/api/class-locator)
        value = self.page.evaluate(
            "(el, prop) => window.getComputedStyle(el).getPropertyValue(prop)",
            css_value,
        )
        value = (value or "").strip()
        return value if value != "" else "Invalid property" 

    def get_cell_data(
        self, 
        row: int,
        col: int,
        locator: str = "tr",
    ) -> str:
        """Get cell text from row/col in a self.page-like locator."""
        val =  self.page.locator(locator).nth(row).locator("td").nth(col).inner_text()
        return str(val)

    def get_row_data(
        self, 
        row: int,
        locator: str = "tr",
    ) :
        """Return all inner texts in the row (like TS allInnerTexts)."""
        return self.page.locator(locator).nth(row).all_inner_texts()  # [1](https://playwright.dev/python/docs/api/class-locator)

    def get_row_data_as_array(
        self, 
        row: int,
        locator: str = "tr",
    ) :
        """Return each TD's inner_text in a row as a list."""
        row_loc = self.page.locator(locator).nth(row)
        count =  row_loc.locator("td").count()
        arr: List[str] = []
        for i in range(count):
            txt =  row_loc.locator("td").nth(i).inner_text()
            arr.append(str(txt))
        return arr

    def get_all_rows_column_data(
        self,
        
        column: int,
        locator: str = "tr",
        number_of_rows: int = 0,
    ) :
        """Return data for a single column from all (or first N) rows."""
        arr: List[str] = []
        actual_len = self.page.locator(locator).count()  # [1](https://playwright.dev/python/docs/api/class-locator)
        length = actual_len if number_of_rows == 0 else min(actual_len, number_of_rows)

        for i in range(length):
            text = self.page.locator(locator).nth(i).locator("td").nth(column).inner_text()
            arr.append(text)
        return arr

    def get_header_names(self) :
        """Return all header names (<th>) as list."""
        return self.page.locator("th").all_inner_texts()  # [1](https://playwright.dev/python/docs/api/class-locator)

    def get_row(self,  index: int, locator: str = "tr") -> Locator:
        """Return row locator at index."""
        return self.page.locator(locator).nth(index)

    def get_header_column_number(
        self,
        col_name: str,
        exact_match: bool = False,
    ) -> int:
        """Return index of header with matching name; -1 if not found."""
        headers = self.page.locator("th").all_inner_texts()  # [1](https://playwright.dev/python/docs/api/class-locator)
        target = col_name.strip()
        if exact_match:
            return next((i for i, h in enumerate(headers) if h.strip() == target), -1)
        return next((i for i, h in enumerate(headers) if h.strip().lower() == target.lower()), -1)

    def get_header_name(self,  index: int) -> str:
        """Return text of header at index."""
        return self.page.locator("th").nth(index).inner_text()

    def get_meta_rows_length(self,  locator: str = "tr"):
        """Return number of rows. (TS had extra ' tr' - Python keeps it simple.)"""
        return int(self.page.locator(locator).count())  # [1](https://playwright.dev/python/docs/api/class-locator)

    def get_column_length(self,  row_index: int = 0, locator: str = "tr") :
        """Return number of columns (td) in a given row."""
        return int(self.page.locator(locator).nth(row_index).locator("td").count())

    def get_row_column(
        self,
        
        row_index: int,
        column_index: int,
        locator: str = "tr",
    ) -> Locator:
        """Return locator for specific cell (row, col)."""
        return self.page.locator(locator).nth(row_index).locator("td").nth(column_index)

    @staticmethod
    def _normalize_values(values: List[str]) :
        """Trim and remove leading Excel-style apostrophe marker patterns."""
        normalized: List[str] = []
        for v in values:
            t = v.strip()
            if "'" in t:
                parts = t.split("'")
                if len(parts) > 1 and parts[1]:
                    t = parts[1].strip()
                else:
                    t = t.replace("'", "").strip()
            normalized.append(t)
        return normalized

    def get_matched_row_index(
        self,
        
        row_values: List[str],
        locator: str = "tr",
        exact_match: bool = False,
    ) -> int:
        """
        Return index of first row that matches all row_values (exact or contains).
        Returns -1 if none found.
        """
        wanted = self._normalize_values(row_values)

        rows = self.page.locator(locator)
        rows.nth(0).wait_for()  # ensure at least one row exists
        n_rows =  rows.count()  # [1](https://playwright.dev/python/docs/api/class-locator)

        row_text_matrix: List[List[str]] = []
        for i in range(n_rows):
            # More reliable than parsing row.innerText: read per-cell
            cells =  rows.nth(i).locator("td").all_inner_texts()
            cells = [c.strip() for c in cells if c is not None]
            if len(cells) > 1:
                row_text_matrix.append(cells)

        def matches(row_cells: List[str]) -> bool:
            for col_data in wanted:
                if exact_match:
                    if not any(cell.strip().lower() == col_data.strip().lower() for cell in row_cells):
                        return False
                else:
                    if not any(col_data.strip().lower() in cell.strip().lower() for cell in row_cells):
                        return False
            return True

        for idx, row_cells in enumerate(row_text_matrix):
            if matches(row_cells):
                return idx
        return -1

    def get_matched_row_indices(
        self,
        
        row_values: List[str],
        locator: str = "tr",
        exact_match: bool = False,
    ) -> List[int]:
        """Return indices of all rows that match all row_values."""
        wanted = self._normalize_values(row_values)
        found: List[int] = []

        rows = self.page.locator(locator)
        n_rows =  rows.count()  # [1](https://playwright.dev/python/docs/api/class-locator)

        for i in range(n_rows):
            cells =  rows.nth(i).locator("td").all_inner_texts()
            row_cells = [c.strip() for c in cells if c is not None]

            ok = True
            for col_data in wanted:
                if exact_match:
                    if not any(cell.lower() == col_data.lower() for cell in row_cells):
                        ok = False
                        break
                else:
                    if not any(col_data.lower() in cell.lower() for cell in row_cells):
                        ok = False
                        break

            if ok:
                found.append(i)

        return found

    def get_meta_page_matched_row_index(
        self,
        
        row_values: List[str],
        locator: str = "tr",
        exact_match: bool = False,
    ) -> int:
        """Same as get_matched_row_index but keeps TS naming."""
        return  self.get_matched_row_index(self.page, row_values, locator=locator, exact_match=exact_match)

    def get_meta_matched_row_indices(
        self,
        
        row_values: List[str],
        locator: str = "tr",
        exact_match: bool = False,
        min_column_size: int = 1,
    ) -> List[int]:
        """
        Equivalent of TS getMetaself.pageMatchedRowIndices:
        - builds row arrays from td texts
        - filters rows by min_column_size
        - returns all matched indices (prevent duplicates by clearing matched rows)
        """
        wanted = self._normalize_values(row_values)
        found_indices: List[int] = []

        rows = self.page.locator(locator).all()  # locator.all() exists in Python [1](https://playwright.dev/python/docs/api/class-locator)

        matrix: List[List[str]] = []
        for row in rows:
            cols =  row.locator("td").all()
            row_cells: List[str] = []
            for col in cols:
                row_cells.append(( col.inner_text()).strip())

            if len(row_cells) > min_column_size:
                matrix.append(row_cells)

        def matches(row_cells: List[str]) -> bool:
            for col_data in wanted:
                if exact_match:
                    if not any(cell.lower() == col_data.lower() for cell in row_cells):
                        return False
                else:
                    if not any(col_data.lower() in cell.lower() for cell in row_cells):
                        return False
            return True

        # emulate TS behavior: find all matches, prevent matching same row twice
        for _ in range(len(matrix)):
            idx = next((i for i, row_cells in enumerate(matrix) if matches(row_cells)), -1)
            if idx >= 0:
                found_indices.append(idx)
                matrix[idx] = []  # clear to avoid matching again
            else:
                break

        return found_indices

    def is_exist(self, root: Locator, selector: str) -> bool:
        """Return True if at least one element exists under root."""
        return ( root.locator(selector).count()) > 0  # [1](https://playwright.dev/python/docs/api/class-locator)
