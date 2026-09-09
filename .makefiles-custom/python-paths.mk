# No src/ package — ruff the templates and tests. mypy only tests/: four
# spider.py files share a module name and cannot be type-checked together.
SRC_DIR := spiders
TEST_DIR := tests
PYTHON_RUFF_PATHS := spiders tests
MYPY_ARGS := tests
