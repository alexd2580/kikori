.PHONY: run
run:
	@poetry run kikori

.PHONY: mypy
mypy:
	@poetry run mypy kikori
