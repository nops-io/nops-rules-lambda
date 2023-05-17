test:
	rm -rf venv
	python3 -m venv venv
	. venv/bin/activate; pip install -r ./src/nswitch_scheduler/requirements.txt -r ./src/nswitch_scheduler/requirements.dev.txt; cd src/nswitch_scheduler; pytest
	rm -rf venv

test_essential:
	rm -rf venv
	python3 -m venv venv
	. venv/bin/activate; pip install -r ./src/nswitch_essential/requirements.txt -r ./src/nswitch_essential/requirements.dev.txt; cd src/nswitch_essential; pytest
	rm -rf venv

environment:
	python3 -m venv env
	. env/bin/activate; pip install -r ./src/nswitch_scheduler/requirements.txt -r ./src/nswitch_scheduler/requirements.dev.txt; 

environment_essential:
	python3 -m venv env
	. env/bin/activate; pip install -r ./src/nswitch_essential/requirements.txt -r ./src/nswitch_essential/requirements.dev.txt; 
