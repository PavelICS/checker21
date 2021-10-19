import re
import json
from os import PathLike
from pathlib import Path
from typing import Optional, Union, List, Dict, Any, Iterable

from checker21.core import Project
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


class NorminetteState:
    path: Path
    result: Dict[str, NorminetteFileCheckResult]
    files: Dict[str, Dict[str, Any]]  # TODO convert file info to TypedDict

    def __init__(self, state: Dict, *, path: Path):
        self.path = path
        _files = state.get("files")
        if _files:
            self.files = {file['name']: file for file in _files}
        else:
            self.files = {}
        self.result = state.get("result") or {}

    def save(self):
        with self.path.open("w") as stream:
            json.dump(self.serialize(), stream, ensure_ascii=False, indent=4)

    @classmethod
    def load(cls, path: Path) -> 'NorminetteState':
        if path.exists():
            with path.open() as stream:
                state = json.load(stream)
        else:
            state = {}
        return cls(state, path=path)

    def is_file_changed(self, file: Union[PathLike, str]) -> bool:
        path = Path(file)
        stat = path.stat()
        filename = str(file)
        file_info = self.files.get(filename)

        try:
            ctime = stat.st_birthtime
        except AttributeError:
            ctime = stat.st_ctime

        if not file_info:
            self.files[filename] = {
                "name": filename,
                "ctime": ctime,
                "mtime": stat.st_mtime,
            }
            return True
        if file_info["ctime"] == ctime and file_info["mtime"] == stat.st_mtime:
            return False
        file_info["ctime"] = ctime
        file_info["mtime"] = stat.st_mtime
        return True

    def validate_cached_files(self, files: Iterable[Path]):
        files_set = {str(file) for file in files}
        self.files = {file: info for file, info in self.files.items() if file in files_set}

    def serialize(self):
        serialized = {}
        if self.files:
            serialized["files"] = list(self.files.values())
        serialized["result"] = self.result
        return serialized


class Norminette:
    _cmd_name: str = "norminette"
    state: Optional[NorminetteState]
    _version: Optional[str]

    def __init__(self):
        self._version = None
        self.state = None

    @classmethod
    def load(cls, path: Path) -> 'Norminette':
        state = NorminetteState.load(path)
        self = cls()
        self.state = state
        return self

    def save(self, path: Optional[Path] = None):
        if path:
            self.state.path = path
        self.state.save()

    @property
    def version(self) -> Optional[str]:
        if self._version is not None:
            return self._version
        try:
            cmd = bash([self._cmd_name, "-v"], echo=False)
        except FileNotFoundError:
            return None
        if cmd.stderr:
            return None
        output = cmd.stdout.strip().decode()
        try:
            version = output.split(' ', 1)[1]
        except IndexError:
            raise NorminetteException(f"Failed to parse norminette version from `{output}`")
        self._version = version
        return version

    def run(
            self,
            files: Optional[Union[List[str], str, List[Path], Path]] = None
    ) -> Dict[str, NorminetteFileCheckResult]:
        if files:
            if isinstance(files, (str, PathLike)):
                files = [files]
            files = [str(x) for x in files]
            cmd = bash([self._cmd_name, *files], echo=False)
        else:
            cmd = bash([self._cmd_name], echo=False)
        if cmd.stderr:
            raise NorminetteException(cmd.stderr.decode())
        output = cmd.stdout.strip().decode()
        return self.parse_output(output)

    def get_project_files(self, project: Project) -> List[Path]:
        return [file for file in project.list_files() if file.suffix == ".c" or file.suffix == ".h"]

    def check_project(self, project: Project) -> Dict[str, NorminetteFileCheckResult]:
        files = self.get_project_files(project)
        self.state.validate_cached_files(files)
        files = [file for file in files if self.state.is_file_changed(file)]
        if files:
            result = self.run(files)
            self.state.result.update(result)
        else:
            result = self.state.result
        return result

    def parse_output(self, output: str) -> Dict[str, NorminetteFileCheckResult]:
        result = parse_norminette_output(output)
        return result


def get_norminette_version() -> Optional[str]:
    return Norminette().version


def run_norminette(
        files: Optional[Union[List[str], str, List[Path], Path]] = None
) -> Dict[str, NorminetteFileCheckResult]:
    return Norminette().run(files)


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
        line = line.strip()
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

        if line.startswith("\x1b[31m"):
            line = line.replace("\t\x1b[31m", '').replace("\x1b[0m'", '')
            add_error(line)
            continue

        if line.startswith("Missing"):
            last_warning = line
            continue

        raise NorminetteException(f"Failed to parse line `{line}`")

    return result


class NorminetteError:
    code: str
    line: int
    col: int
    description: str
    raw: str

    __slots__ = ("code", "line", "col", "description", "raw")

    def __init__(self, code: str, line: int, col: int, description: str, raw: str):
        self.code = code
        self.line = line
        self.col = col
        self.description = description
        self.raw = raw

    @classmethod
    def parse(cls, error: str) -> Optional['NorminetteError']:
        match = re.match(r"Error:\s+([\w_]+)\s+\(line:\s*(\d+),\s*col:\s*(\d+)\):(.*)", error)
        if match:
            return NorminetteError(
                code=match.group(1),
                line=int(match.group(2)),
                col=int(match.group(3)),
                description=match.group(4).strip(),
                raw=error,
            )

    def __str__(self) -> str:
        return self.raw
