
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union


class DataBaseUtils:
    """
    Python rewrite of the TS DataBaseUtils.

    - db_type: "oracle" | "mysql" | "sql"
    - db_config: dict-like configuration, depends on driver.
    - query_result: dict containing:
        - rows: list of row tuples
        - metaData: list of dicts with at least {"name": <colname>}
        - json: list[dict] (only when casesync=False for Oracle, like TS)
    """

    def __init__(self, db_type: str, db_config: Optional[Dict[str, Any]] = None):
        self.db_conn: Any = None  # underlying connection object
        self.conn: Any = None     # kept for parity with TS; not strictly required
        self.db_type: str = db_type
        self.db_config: Dict[str, Any] = db_config or {}
        self.query_result: Optional[Dict[str, Any]] = None

    def set_db_type(self, db_type: str) -> None:
        self.db_type = db_type

    def set_config(self, db_config: Dict[str, Any]) -> None:
        self.db_config = db_config

    def execute_select_cmd(
        self,
        query: str,
        params: Optional[Union[Sequence[Any], Dict[str, Any]]] = None,
        *,
        casesync: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute a SELECT query and return a query_result dict.

        Args:
            query: SQL query string
            params: optional bind params (tuple/list for positional or dict for named)
            casesync: if False, also populate query_result["json"] (Oracle behavior parity)

        Returns:
            query_result dict with "rows", "metaData", and possibly "json".
        """
        dbt = (self.db_type or "").lower().strip()

        if dbt == "oracle":
            return self._execute_oracle_select(query, params=params, casesync=casesync)

        if dbt == "mysql":
            return self._execute_mysql_select(query, params=params)

        if dbt == "sql":
            # Your TS class constructor allows "sql" but code doesn't implement it.
            # You can implement using pyodbc or pymssql if needed.
            raise NotImplementedError(
                "db_type='sql' is not implemented. "
                "Use pyodbc/pymssql and add a _execute_sqlserver_select method."
            )

        raise ValueError(f"Unsupported db_type: {self.db_type!r}")

    # -----------------------------
    # Oracle implementation
    # -----------------------------
    def _execute_oracle_select(
        self,
        query: str,
        params: Optional[Union[Sequence[Any], Dict[str, Any]]] = None,
        *,
        casesync: bool,
    ) -> Dict[str, Any]:
        """
        Oracle select using python-oracledb.

        Expected db_config keys commonly include:
            user, password, dsn
        Optional:
            config_dir, wallet_location, wallet_password, etc.
        """
        try:
            import oracledb  # python-oracledb
        except ImportError as e:
            raise ImportError(
                "Missing dependency: 'oracledb'. Install with: pip install oracledb"
            ) from e

        conn = None
        cur = None
        try:
            conn = oracledb.connect(**self.db_config)
            cur = conn.cursor()
            if params is None:
                cur.execute(query)
            else:
                cur.execute(query, params)

            rows = cur.fetchall()
            # cur.description is list of tuples: (name, type_code, display_size, internal_size, precision, scale, null_ok)
            meta = [{"name": d[0]} for d in (cur.description or [])]

            self.query_result = {
                "rows": rows,
                "metaData": meta,
            }

            # Match your TS behavior: build JSON unless casesync is True
            if not casesync:
                self.query_result["json"] = self._results_to_json(rows, meta)

            return self.query_result

        except Exception as err:
            # Match the "Ouch!" console log vibe but raise for caller visibility
            print("Ouch!", err)
            raise
        finally:
            # Always clean up
            try:
                if cur is not None:
                    cur.close()
            finally:
                if conn is not None:
                    conn.close()

    # -----------------------------
    # MySQL implementation
    # -----------------------------
    def _execute_mysql_select(
        self,
        query: str,
        params: Optional[Union[Sequence[Any], Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        MySQL select using mysql-connector-python.

        Expected db_config keys commonly include:
            host, user, password, database, port
        """
        try:
            import mysql.connector as mysql_connector  # mysql-connector-python
        except ImportError:
            try:
                import pymysql as mysql_connector  # PyMySQL fallback
            except ImportError as e:
                raise ImportError(
                    "Missing dependency: 'mysql-connector-python' or 'PyMySQL'. "
                    "Install with: pip install mysql-connector-python pymysql"
                ) from e

        conn = None
        cur = None
        try:
            conn = mysql.connector.connect(**self.db_config)
            cur = conn.cursor()

            if params is None:
                cur.execute(query)
            else:
                cur.execute(query, params)

            rows = cur.fetchall()
            # cursor.description is tuples; name is index 0
            meta = [{"name": d[0]} for d in (cur.description or [])]

            self.query_result = {
                "rows": rows,
                "metaData": meta,
                # TS mysql path returned rows directly, but we keep consistent structure
                "json": self._results_to_json(rows, meta),
            }
            return self.query_result

        except Exception as err:
            print("Ouch!", err)
            raise
        finally:
            try:
                if cur is not None:
                    cur.close()
            finally:
                if conn is not None:
                    conn.close()

    # -----------------------------
    # Helper (like getResultsToJson)
    # -----------------------------
    def _results_to_json(self, rows: List[tuple], meta_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert rows + metaData into list of dicts.

        TS version built JSON via string concatenation + JSON.parse.
        Python version safely builds dicts directly.
        """
        col_names = [m.get("name") for m in meta_data]
        result: List[Dict[str, Any]] = []
        for row in rows:
            item = {col_names[i]: row[i] for i in range(len(col_names))}
            result.append(item)
        return result
