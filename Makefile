

clean::
	@echo "Cleaning generated files..."
	@rm -rf .coverage
	@rm -rf ./pytest
	@echo "Done!"


env::
	@echo "Pulling environment variables..."
	@npx dotenv-vault pull development .env
	@npx dotenv-vault pull local .env.local
	@echo "Done!"

lint::
	@echo "Linting source files..."
	@poetry run flake8 .
	@echo "Done!"

poetry::
	@echo "Creating virtual environment..."
	@poetry install
	@echo "Done!"

test::
	@echo "Running tests"
	@poetry run -- pytest -v
	@echo "Done!"
