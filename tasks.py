import test

from invoke import Collection, task


@task
def format(c):
    c.run(
        """
        poetry install
        poetry run isort -l 88 --up --tc --float-to-top src tests
        poetry run black src tests
        poetry run ruff src tests
        poetry run flake8 src tests
        """
    )


@task
def edge(c):
    c.run(
        """
    edgedb-py --target async --file
    edgedb-py --target blocking --no-skip-pydantic-validation --file
    cp generated_async_edgeql.py src/wat/data/queries_async.py
    cp generated_edgeql.py src/wat/data/queries_blocking.py
    poetry install
    python edge_model_gen.py
    echo import pydantic > pd_import
    cat pd_import generated_async_edgeql.py models.py > src/wat/data/queries_async.py && rm generated_async_edgeql.py
    cat pd_import generated_edgeql.py models.py > src/wat/data/queries_blocking.py && rm generated_edgeql.py models.py
    isort --float-to-top src/wat/data/queries_async.py src/wat/data/queries_blocking.py
    python edge_dataclass_to_pydantic.py
    black src/wat/data/queries_async.py src/wat/data/queries_blocking.py
    rm pd_import
    """  # noqa E501: line too long
    )


@task
def edge_single(c):
    c.run(
        """
    edgedb-py --target async
    """
    )
    import glob

    import edge_model_gen as emg

    for file in glob.glob("queries/*async_edgeql.py"):
        output = "\nimport pydantic\n"
        output += emg.execute(file)
        with open(file, "a") as f:
            f.write(output)

    c.run(
        f"""
    poetry install
    isort --float-to-top queries
    black queries
    """  # noqa E501: line too long
    )


namespace = Collection(format, edge, test, edge_single)
