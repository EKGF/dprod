
build:
	python3 -m venv .venv
	source .venv/bin/activate ; python3 -m pip install --upgrade pip
	source .venv/bin/activate ; python3 -m pip install -r requirements.txt
	source .venv/bin/activate ; python3 spec-generator.py
