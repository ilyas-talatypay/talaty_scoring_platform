import json
from pathlib import Path
from tempfile import TemporaryDirectory

from api.openapi_export import export_openapi
from core.schema_export import export_schemas


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def test_core_schemas_match_checked_in() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    schemas_dir = repo_root / "schemas" / "v0"

    with TemporaryDirectory() as tmp_dir:
        export_dir = Path(tmp_dir)
        export_schemas(export_dir)

        for exported_path in export_dir.glob("*.json"):
            checked_in_path = schemas_dir / exported_path.name
            assert checked_in_path.exists(), f"Missing checked-in schema {exported_path.name}"
            assert _load_json(exported_path) == _load_json(checked_in_path)


def test_openapi_matches_checked_in() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checked_in_path = repo_root / "schemas" / "v0" / "openapi.json"

    with TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "openapi.json"
        export_openapi(output_path)
        assert _load_json(output_path) == _load_json(checked_in_path)
