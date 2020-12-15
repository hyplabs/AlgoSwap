deploy: venv/bin/activate
	. ./config.sh; . venv/bin/activate; python3 deploy.py

venv/bin/activate: requirements.txt
	rm -rf venv; python3 -m venv venv; . venv/bin/activate; python3 -m pip install -r requirements.txt
