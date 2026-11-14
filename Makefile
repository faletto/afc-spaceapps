PY := .venv/bin/python
.PHONY: setup stub fetch data validate test app demo
setup:
	uv venv --python 3.11 && uv pip install -e "pipeline[dev]"
	@if [ -f app/package.json ]; then cd app && npm ci; fi
stub:
	$(PY) -m lunar_listings stub
fetch:
	$(PY) -m lunar_listings fetch
data:
	$(PY) -m lunar_listings data
validate:
	$(PY) -m lunar_listings validate
test:
	cd pipeline && ../$(PY) -m pytest -q --maxfail=1
	@if [ -f app/package.json ]; then cd app && npm test -- --silent; fi
app:
	cd app && npm run build
demo:
	cd app && npm run preview
