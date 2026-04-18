set shell := ["bash", "-cu"]

python := "python3"
venv_dir := ".venv"
activate := "source " + venv_dir + "/bin/activate"

setup:
    {{python}} -m venv {{venv_dir}}
    {{activate}} && pip install --upgrade pip
    {{activate}} && pip install -e '.[dev]'

serve config="config.example.yaml":
    {{activate}} && uvicorn meshshare.app:create_app --factory --host 0.0.0.0 --port 8080 --reload --env-file /dev/null

test:
    {{activate}} && pytest -q

lint:
    {{activate}} && python -m compileall src tests
