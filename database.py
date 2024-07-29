import sqlalchemy
import pandas
import time
from . import logging


def new_database_engine(
    user="",
    password="",
    host="",
    port="",
    database="",
    socket="",
    test_connection_timeout=10,  # second
    test_connection_retry_interval=1,  # second
):
    pre_port = {0: ""}.get(len(port), ":")
    url = f"postgresql://{user}:{password}@{host}{pre_port}{port}/{database}{socket}"
    engine = sqlalchemy.create_engine(url)
    start = time.time()
    while True:
        try:
            test_connection(engine)
            break
        except Exception as e:
            logging.warning(e)
        time.sleep(test_connection_retry_interval)
        assert time.time() - start < test_connection_timeout, "timeout"
    return engine


def test_connection(database_engine):
    with database_engine.connect() as connection:
        assert connection.execute(
            sqlalchemy.text(
                """
            select true;
        """
            )
        ).all()[0][0]


def query_to_df(engine=None, query=None, args=None, return_rows=True):
    assert engine
    assert query
    if args == None:
        args = {}
    with engine.connect() as connection:
        transaction = connection.begin()
        q = connection.execute(sqlalchemy.text(query), args)
        if return_rows:
            data = q.all()
            head = q.keys()
            transaction.commit()
            return pandas.DataFrame(data, columns=head)
        else:
            transaction.commit()
            return None


def query_to_dicts(*args, **kwargs):
    return query_to_df(*args, **kwargs).to_dict("records")


def run_query(engine=None, query=None, args=None):
    return query_to_df(engine, query, args, return_rows=False)
