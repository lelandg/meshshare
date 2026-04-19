set shell := ["bash", "-cu"]

python := "python3"
venv_dir := ".venv"
activate := "source " + venv_dir + "/bin/activate"

# Show available recipes
default:
    @just --list

# Create venv and install dependencies
setup:
    {{python}} -m venv {{venv_dir}}
    {{activate}} && pip install --upgrade pip
    {{activate}} && pip install -e '.[dev]'

# Start the dev server (optionally pass a config file)
serve config="config.example.yaml":
    {{activate}} && uvicorn meshshare.app:create_app --factory --host 0.0.0.0 --port 8080 --reload --env-file /dev/null

# Run tests
test:
    {{activate}} && pytest -q

# Lint/syntax-check source
lint:
    {{activate}} && python -m compileall src tests
