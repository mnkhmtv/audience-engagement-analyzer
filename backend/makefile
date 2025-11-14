#!make

.PHONY: run
run:
@uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: init-alembic
init-alembic:
@alembic init alembic

.PHONY: migration-create
migration-create:
@alembic revision --autogenerate -m "$(name)"

.PHONY: migration-up
migration-up:
@alembic upgrade head

.PHONY: migration-down
migration-down:
@alembic downgrade -1
