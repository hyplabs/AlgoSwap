deploy: venv/bin/activate
	. ./config.sh; . venv/bin/activate; python3 deploy.py

add_liq_test: venv/bin/activate
	. ./config.sh; . venv/bin/activate; python3 tests/add_liquidity_test.py

withdraw_liq_test: venv/bin/activate
	. ./config.sh; . venv/bin/activate; python3 tests/withdraw_liquidity_test.py

swap_t1_for_t2_test: venv/bin/activate
	. ./config.sh; . venv/bin/activate; python3 tests/swap_t1_for_t2_test.py

venv/bin/activate: requirements.txt
	rm -rf venv; python3 -m venv venv; . venv/bin/activate; python3 -m pip install -r requirements.txt
