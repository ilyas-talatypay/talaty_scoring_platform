import json
from pathlib import Path

from api.main import app


def _default_output_path() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "schemas" / "v0" / "openapi.json"


def export_openapi(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n")


def main() -> None:
    export_openapi(_default_output_path())


if __name__ == "__main__":
    main()
