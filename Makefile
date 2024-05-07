.PHONY: run clean docs

black:
	black alchemy

test:
	coverage run -m pytest tests && coverage html && open htmlcov/index.html

type-check:
	mypy alchemy

