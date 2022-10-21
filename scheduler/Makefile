test:
	rm -rf venv
	python3 -m venv venv
	. venv/bin/activate; pip install -r ./src/requirements.txt -r ./src/requirements.dev.txt; cd src; pytest
	rm -rf venv

environment:
	python3 -m venv env
	. env/bin/activate; pip install -r ./src/requirements.txt -r ./src/requirements.dev.txt; 
