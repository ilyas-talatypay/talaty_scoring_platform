.PHONY: lint format test

lint:
	ruff check .

format:
	ruff format .

test:
	python - <<'PY'
from pathlib import Path
if not any(Path('.').rglob('test_*.py')):
    print('No tests found; skipping.')
    raise SystemExit(0)
PY
	pytest -q

