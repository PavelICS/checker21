from os import PathLike
from pathlib import Path
from typing import Optional, Union, List, Dict

from checker21.utils.bash import bash


class NorminetteException(Exception):
    pass


class NorminetteCheckStatus:
    OK          = "ok"
    ERROR       = "error"
    NOT_VALID   = "not valid"


try:
    from typing import TypedDict

    class NorminetteFileCheckResult(TypedDict, total=False):
        status: str
        line: str
        errors: List[str]
        warnings: List[str]
except ImportError:
    TypedDict = None
    NorminetteFileCheckResult = Dict


def get_norminette_version() -> Optional[str]:
    try:
        cmd = bash(["norminette", "-v"], echo=False)
    except FileNotFoundError:
        return None
    if cmd.stderr:
        return None
    output = cmd.stdout.strip().decode()
    try:
        version = output.split(' ', 1)[1]
    except IndexError:
        raise NorminetteException(f"Failed to parse norminette version from `{output}`")
    return version


def run_norminette(
        files: Optional[Union[List[str], str, List[Path], Path]] = None
) -> Dict[str, NorminetteFileCheckResult]:
    if files:
        if isinstance(files, (str, PathLike)):
            files = [files]
        cmd = bash(["norminette", *files], echo=False)
    else:
        cmd = bash(["norminette"], echo=False)
    if cmd.stderr:
        raise NorminetteException(cmd.stderr.decode())
    output = cmd.stdout.strip().decode()
    return parse_norminette_output(output)


def parse_norminette_output(output: str) -> Dict[str, NorminetteFileCheckResult]:
    result = {}

    filename = None
    active_record: Optional[NorminetteFileCheckResult] = None
    last_warning = None

    def add_error(error):
        if not active_record or "errors" not in active_record:
            raise NorminetteException(f"Couldn't add errors to `{filename}`")
        active_record["errors"].append(error)

    def add_record(record):
        nonlocal last_warning

        result[filename] = record
        if last_warning:
            active_record["warnings"] = [last_warning]
            last_warning = None


    for line in output.split("\n"):
        if line.endswith("OK!"):
            filename = line.rsplit(':', 1)[0]
            active_record = {
                "status": NorminetteCheckStatus.OK,
                "line": line,
            }
            add_record(active_record)
            continue

        if line.endswith("Error!"):
            filename = line.rsplit(':', 1)[0]
            active_record = {
                "status": NorminetteCheckStatus.ERROR,
                "line": line,
                "errors": [],
            }
            add_record(active_record)
            continue

        if line.startswith("Error:"):
            if line.endswith("is not valid C or C header file"):
                filename = line.split(':', 1)[0].rsplit('is', 1)[0]
                result[filename] = {
                    "status": NorminetteCheckStatus.NOT_VALID,
                    "line": line,
                }
                continue

            add_error(line)
            continue

        if line.startswith("\t\x1b[31m"):
            line = line.replace("\t\x1b[31m", '').replace("\x1b[0m'", '')
            add_error(line)
            continue

        if line.startswith("Missing"):
            last_warning = line
            continue

        raise NorminetteException(f"Failed to parse line `{line}`")

    return result
