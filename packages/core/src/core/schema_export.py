import argparse
import json
from pathlib import Path

from core.domain.v0 import (
    Dataset,
    DatasetVersion,
    Feature,
    FeatureSet,
    FeatureSetVersion,
    Model,
    Run,
    RunSpec,
)


SCHEMAS = {
    "dataset": Dataset,
    "dataset_version": DatasetVersion,
    "feature": Feature,
    "feature_set": FeatureSet,
    "feature_set_version": FeatureSetVersion,
    "run_spec": RunSpec,
    "run": Run,
    "model": Model,
}


def export_schemas(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle = {"version": "v0", "schemas": {}}
    for name, model in SCHEMAS.items():
        schema = model.model_json_schema()
        bundle["schemas"][name] = schema
        (output_dir / f"{name}.json").write_text(
            json.dumps(schema, indent=2, sort_keys=True) + "\n"
        )
    (output_dir / "bundle.json").write_text(
        json.dumps(bundle, indent=2, sort_keys=True) + "\n"
    )


def _default_output_dir() -> Path:
    # repo_root/schemas/v0
    repo_root = Path(__file__).resolve().parents[4]
    return repo_root / "schemas" / "v0"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export domain JSON schemas.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_default_output_dir(),
        help="Directory to write JSON schema files.",
    )
    args = parser.parse_args()
    export_schemas(args.output_dir)


if __name__ == "__main__":
    main()

