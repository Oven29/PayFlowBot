dev:
	python main.py

migrate:
	alembic upgrade head

# create-migration msg="comment (optional)"
create-migration:
	alembic revision --autogenerate -m "$(msg)"

# Workaround for passing arguments to `make`
%:
	@:
