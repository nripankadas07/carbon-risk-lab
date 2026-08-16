.PHONY: test demo golden check

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

demo:
	PYTHONPATH=src python3 -m carbon_risk_lab demo --simulations 1000 --output-dir reports

golden:
	PYTHONPATH=src python3 -m carbon_risk_lab demo --simulations 1000 --output-dir artifacts/demo

check:
	python3 -m compileall -q src tests
