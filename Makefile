.PHONY: dev

_fmt_check:
	poetry run ruff format . --check --diff

_fix_check:
	poetry run ruff check .

_mypy:
	poetry run mypy ./

lint:
	make -j _fmt_check _fix_check _mypy

_ruff_format_apply:
	poetry run ruff format

fmt:
	poetry run ruff format .

fix:
	poetry run ruff check . --fix
