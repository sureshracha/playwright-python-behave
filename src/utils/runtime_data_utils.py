
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import file_utils as fileUtils
import test_context as tcontext


DEFAULT_INITIAL_DATA = {
    "testData": [],
    "pickedMemberData": [],
    "pickedFacilityData": [],
    "authsData": {},
}


def create_run_time_data_json_file(
    r_filename: Any,
    run_time_data_folder: str,
    environment: str,
    initial_data: Union[str, Dict[str, Any]] = DEFAULT_INITIAL_DATA,
) -> str:
    """
    TS: createRunTimeDataJsonFie

    - Ensures runtime folder exists
    - Builds filename: <folder>/<environment>-<basefilename>.json
    - Creates file with initial_data if it does not exist
    - Returns the absolute/relative filename string
    """
    fileUtils.check_folder_and_create(run_time_data_folder)

    base_name = get_run_time_data_file_name(r_filename)
    filename = str(Path(run_time_data_folder) / f"{environment}-{base_name}.json")

    if not Path(filename).exists():
        # initial_data may be a JSON string or dict
        if isinstance(initial_data, str):
            Path(filename).write_text(initial_data, encoding="utf-8")
        else:
            Path(filename).write_text(json.dumps(initial_data, indent=2), encoding="utf-8")

    return filename


def get_run_time_data_file_name(filepath: Any) -> str:
    """
    TS: getRunTimeDataFileName
    Returns basename for paths containing / or \\.
    """
    s = str(filepath)
    # Path handles both types; but keep TS-like behavior explicit
    return s.split("/")[-1] if "/" in s else s.split("\\")[-1]


def get_run_time_scenario_no(filepath: Any) -> str:
    """
    TS: getRunTimeScnearioNo

    - Prints first character (like console.log(filename.substring(0,1)))
    - Returns first segment before '-' trimmed (always, since split length > 0)
      fallback: first char if no '-'
    """
    filename = get_run_time_data_file_name(filepath)
    print(filename[:1])

    parts = filename.split("-")
    return parts[0].strip() if len(parts) > 0 else filename[:1]


def get_run_time_data_file_path() -> str:
    """
    TS: getRunTimeDataFilePath
    """
    if tcontext.testContext is None:
        raise RuntimeError("testContext is not configured.")
    return tcontext.testContext.runtime_storage_file


def _load_runtime_json() -> Dict[str, Any]:
    """
    Helper: read the runtime storage JSON
    """
    runtime_file = get_run_time_data_file_path()
    return fileUtils.read_json_data(runtime_file)


def _save_runtime_json(data: Dict[str, Any]) -> None:
    """
    Helper: write the runtime storage JSON
    """
    runtime_file = get_run_time_data_file_path()
    fileUtils.write_json_data(runtime_file, data)


def set_run_time_data(key: str, value: Any) -> None:
    """
    TS: setRunTimeData
    """
    run_time_data = _load_runtime_json()
    run_time_data[key] = value
    _save_runtime_json(run_time_data)


def remove_run_time_data(key: str) -> None:
    """
    TS: removeRunTimeData
    """
    run_time_data = _load_runtime_json()
    run_time_data.pop(key, None)
    _save_runtime_json(run_time_data)


def set_run_time_scenario_data(
    key: str,
    value: Any,
    testdata_index: int = 0,
    key_array_name: str = "testData",
) -> None:
    """
    TS: setRunTimeScenarioData

    If testData has entries:
      runtime[key_array_name][testdata_index][key] = value
    else:
      pushes {"key": "value"} into testData
    """
    run_time_data = _load_runtime_json()

    arr = run_time_data.get(key_array_name, [])
    if isinstance(arr, list) and len(arr) > 0:
        # Ensure index exists
        while len(arr) <= testdata_index:
            arr.append({})
        if not isinstance(arr[testdata_index], dict):
            arr[testdata_index] = {}
        arr[testdata_index][key] = value
    else:
        run_time_data.setdefault("testData", [])
        # TS forced string values via JSON.parse(`{"key":"value"}`)
        run_time_data["testData"].append({key: str(value)})

    run_time_data[key_array_name] = arr if isinstance(arr, list) else run_time_data.get(key_array_name, [])
    _save_runtime_json(run_time_data)


def get_filename_with_scenario_id(key: str, env: str, run_time_data_folder: str) -> Optional[str]:
    """
    TS: getFilenameWithScenarioID
    Finds a file in folder whose name includes f"{env}-{key}"
    Returns filename (not full path). Returns None if not found.
    """
    files_array = fileUtils.get_file_names_from_dir(run_time_data_folder)
    target = f"{env}-{key}"
    for name in files_array:
        if target in name:
            return name
    return None


def get_run_time_data(key: str) -> Any:
    """
    TS: getRunTimeData
    Returns json[key] else ''.
    """
    data = _load_runtime_json()
    return data.get(key, "")


def get_run_time_results_data(key: str) -> Any:
    """
    TS: getRunTimeResultsData
    """
    data = _load_runtime_json()
    return data.get("results", {}).get(key)


def get_run_time_scenario_data(key: str, index: int, key_array_name: str = "testData") -> Any:
    """
    TS: getRunTimeScenarioData
    Logs and returns scenario item value or ''.
    """
    data = _load_runtime_json()
    value = ""
    try:
        value = data[key_array_name][index].get(key, "")
    except Exception:
        value = ""

    print(f"Getting - {key} : {value}")
    return value


def get_run_time_picked_member_data(key: str) -> Any:
    """
    TS: getRunTimePickedMemberData
    """
    data = _load_runtime_json()
    value = data.get("pickedMemberData", {}).get(key)
    print(f"Getting - {key} : {value}")
    return value


def get_run_time_full_picked_member_data() -> Any:
    """
    TS: getRunTimeFullPickedMemberData
    """
    data = _load_runtime_json()
    return data.get("pickedMemberData")


def get_run_time_full_data() -> Dict[str, Any]:
    """
    TS: getRunTimeFullData
    """
    return _load_runtime_json()


def copy_json_specific_data(source: str, destination: str, test_data_index: int) -> None:
    """
    TS: copyJsonSpecificData
    Copies keys from json[source][testDataIndex] to json[destination]
    """
    data = _load_runtime_json()
    src_obj = data.get(source, [])
    if not isinstance(src_obj, list) or len(src_obj) <= test_data_index:
        return

    data.setdefault(destination, {})
    if not isinstance(data[destination], dict):
        data[destination] = {}

    for k, v in src_obj[test_data_index].items():
        data[destination][k] = v

    _save_runtime_json(data)


def get_runtime_scenario_data(key_array_name: str, iteration_count: str, dataset: str) -> Any:
    """
    TS: getRuntimeScenarioData
    Finds object where obj.Iteration == iteration_count and obj.DataSet == dataset
    Returns the object or ''.
    """
    data = _load_runtime_json()
    arr = data.get(key_array_name, [])
    if not isinstance(arr, list):
        return ""

    for obj in arr:
        if str(obj.get("Iteration")) == str(iteration_count) and str(obj.get("DataSet")) == str(dataset):
            return obj
    return ""


def get_runtime_scenario_index(key_array_name: str, iteration_count: str, dataset: str) -> int:
    """
    TS: getRuntimeScenarioIndex
    Returns the index of matching scenario or -1.
    """
    data = _load_runtime_json()
    arr = data.get(key_array_name, [])
    if not isinstance(arr, list):
        return -1

    for i, obj in enumerate(arr):
        if str(obj.get("Iteration")) == str(iteration_count) and str(obj.get("DataSet")) == str(dataset):
            return i
    return -1


def add_or_update_run_time_results_data(key: str, value: Any) -> None:
    """
    TS: addOrUpdateRunTimeResultsData
    """
    data = _load_runtime_json()
    data.setdefault("results", {})
    if not isinstance(data["results"], dict):
        data["results"] = {}
    data["results"][key] = value
    _save_runtime_json(data)


def add_or_update_run_time_scenario_data(array_name: str, index: int, key: str, value: Any) -> None:
    """
    TS: addOrUpdateRunTimeScenarioData
    """
    data = _load_runtime_json()
    data.setdefault(array_name, [])
    arr = data[array_name]
    if not isinstance(arr, list):
        arr = []
        data[array_name] = arr

    while len(arr) <= index:
        arr.append({})

    if not isinstance(arr[index], dict):
        arr[index] = {}

    arr[index][key] = value
    _save_runtime_json(data)


def set_run_time_data_with_pipe_symbol(key: str, value: str) -> None:
    """
    TS: setRunTimeDataWithPipeSynbol
    """
    data = _load_runtime_json()
    if data.get(key) is None:
        data[key] = value
    else:
        data[key] = f"{data[key]}|{value}"
    _save_runtime_json(data)


def set_run_time_data_with_comma(key: str, value: str) -> None:
    """
    TS: setRunTimeDataWithComma
    """
    data = _load_runtime_json()
    if data.get(key) is None:
        data[key] = value
    else:
        data[key] = f"{data[key]},{value}"
    _save_runtime_json(data)


def store_in_runtime_data_file(run_time_data: Dict[str, Any]) -> None:
    """
    TS: storeInRuntimeDataFile

    - Always sets runTimeData.results = {}
    - If runtime file exists:
        - If existing data.testData.length == 0: overwrite file
        - Else: do nothing ("already upto date")
      Else: create file
    """
    runtime_file = get_run_time_data_file_path()
    run_time_data["results"] = {}

    if fileUtils.is_file_exist(runtime_file):
        existing = fileUtils.read_json_data(runtime_file)
        existing_test_data = existing.get("testData", [])
        if isinstance(existing_test_data, list) and len(existing_test_data) == 0:
            Path(runtime_file).write_text(json.dumps(run_time_data, indent=2), encoding="utf-8")
            print(f"\n{runtime_file}  ### file  updated")
        else:
            print(f"{runtime_file}\n file already upto date")
    else:
        Path(runtime_file).write_text(json.dumps(run_time_data, indent=2), encoding="utf-8")
        print(f"{runtime_file} ### file created")


def copy_data_from_source_json_to_runtime_data(
    source_data: Dict[str, Any],
    index: int,
    exclude_keys_list: Any,
    key_array_name: str = "testData",
) -> None:
    """
    TS: copyDatafromSourceJsonToRunTimeData

    exclude_keys_list.copyMyTasksDataKeysForExclude is expected to be a list.
    Copies keys from source_data into runtime[key_array_name][index], excluding keys in exclude list.
    """
    data = _load_runtime_json()
    data.setdefault(key_array_name, [])
    arr = data[key_array_name]
    if not isinstance(arr, list):
        arr = []
        data[key_array_name] = arr

    while len(arr) <= index:
        arr.append({})
    if not isinstance(arr[index], dict):
        arr[index] = {}

    exclude = getattr(exclude_keys_list, "copyMyTasksDataKeysForExclude", []) \
              if exclude_keys_list is not None else []
    exclude = exclude or []

    for k, v in source_data.items():
        if exclude:
            if str(k).strip() not in [str(x).strip() for x in exclude]:
                arr[index][k] = v
        else:
            arr[index][k] = v

    _save_runtime_json(data)


def get_scenarios_data_as_array(file_path: str, test_scenario_id: str) -> List[Dict[str, Any]]:
    """
    TS: getScenariosDataAsArray
    Filters staticData.testData where TestScenario == testScenarioId
    """
    static_data = fileUtils.read_json_data(file_path)
    scenarios: List[Dict[str, Any]] = []

    for scenario_data in static_data.get("testData", []):
        if scenario_data.get("TestScenario") == test_scenario_id:
            scenarios.append(scenario_data)

    return scenarios


def copy_scenarios_data_to_runtime_data_file(test_scenario_id: Any, complete_folder_path: str, source_file: str) -> None:
    """
    TS: copyScenariosDataToRuntimeDataFile

    - For each .json filename in folder:
        - scenarioData = get_scenarios_data_as_array(source_file, test_scenario_id)
        - if scenarioData exists:
            dataArrayKey = filename.replace('D_','').replace('.json','')
            runtime_json[dataArrayKey] = scenarioData
        - write runtime file (TS writes inside loop)
    """
    runtime_file = get_run_time_data_file_path()
    file_names = fileUtils.get_file_names_from_dir(complete_folder_path)
    data = _load_runtime_json()

    for filename in file_names:
        if ".json" in filename:
            scenario_data = get_scenarios_data_as_array(source_file, str(test_scenario_id))
            if scenario_data:
                data_array_key = filename.replace("D_", "").replace(".json", "")
                data[data_array_key] = scenario_data

        if fileUtils.is_file_exist(runtime_file):
            Path(runtime_file).write_text(json.dumps(data, indent=2), encoding="utf-8")


def return_random_number(max_value: int, min_value: int = 0) -> int:
    """
    TS: returnRandomNumber(min=0, max)
    Inclusive range.
    """
    return random.randint(min_value, max_value)
