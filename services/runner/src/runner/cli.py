import argparse
from pathlib import Path

import yaml

from core.domain.v0 import RunSpec
from runner.config import get_settings
from runner.runtime import execute_run_spec
from runner.store import get_store


def _load_spec(path: Path) -> RunSpec:
    payload = yaml.safe_load(path.read_text())
    if "run_spec_id" in payload and "id" not in payload:
        payload["id"] = payload.pop("run_spec_id")
    return RunSpec.model_validate(payload)


def run_from_spec(spec_path: Path) -> int:
    settings = get_settings()
    store = get_store(settings)
    run_spec = _load_spec(spec_path)
    execute_run_spec(settings=settings, store=store, run_spec=run_spec)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="runner")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_cmd = subparsers.add_parser("run", help="Run a spec file")
    run_cmd.add_argument("--spec", required=True, type=Path)

    args = parser.parse_args()

    if args.command == "run":
        run_from_spec(args.spec)


if __name__ == "__main__":
    main()

