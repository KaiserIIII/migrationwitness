import os
import pathlib
import pytest


@pytest.fixture
def pg_bin():
    value=os.environ.get('MW_PG_BIN')
    if not value:
        pytest.skip('MW_PG_BIN unset: actual PostgreSQL NOT RUN')
    return pathlib.Path(value)
