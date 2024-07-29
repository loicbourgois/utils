import sqlalchemy
import pandas
import time
from .log import logging
from .parallel import parallel
from .parallel import async_wrap
from .runcmd import runcmd_list
import re


def get_connection_url(
    user="",
    password="",
    host="",
    port="",
    database="",
    socket="",
):
    return f"postgresql://{user}:{password}@{host}:{port}/{database}{socket}"


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


@async_wrap
def runcmd_list_async(command):
    return "\n".join(
        runcmd_list(
            command,
            quiet=True,
        )
    )


def description(database_url):
    table_list = runcmd_list(
        [
            "psql",
            database_url,
            "-c",
            r"\d",
        ],
        quiet=True,
    )
    commands = []
    for line in table_list[3 : len(table_list) - 2]:
        table_name = line.split("|")[1].strip()
        _d = r"\d"
        commands.append(
            [
                "psql",
                database_url,
                "-c",
                f"{_d} {table_name}",
            ]
        )
    descriptions = parallel(commands, runcmd_list_async)
    description_2 = runcmd_list(
        [
            "psql",
            database_url,
            "-c",
            """
            select n.nspname as enum_schema,  
                t.typname as enum_name,  
                e.enumlabel as enum_value
            from pg_type t
                join pg_enum e on t.oid = e.enumtypid  
                join pg_catalog.pg_namespace n ON n.oid = t.typnamespace
            order by enum_schema, enum_name, enum_value
            ;
        """,
        ],
        quiet=True,
    )
    return (
        "Tables:\n" + "\n".join(descriptions) + "\nEnums:\n" + "\n".join(description_2)
    )


def mermaid_simple(x):
    table = ""
    lines = ["flowchart LR"]
    for l in x.split("\n"):
        pattern = r'Table "public\.(\w+)"'
        for match in re.findall(pattern, l):
            if match != table:
                table = match
                lines.append(f"{table}")
    pattern = r'TABLE "(\w+)" CONSTRAINT "(\w+)" FOREIGN KEY \((\w+)\) REFERENCES (\w+)\((\w+)\)'
    connections = {}
    for match in re.findall(pattern, x):
        ref = {
            "table": match[0],
            "constraint": match[1],
            "foreign_key": match[2],
            "reference_table": match[3],
            "reference_column": match[4],
        }
        connections[f"{ref['table']} -.- {ref['reference_table']}"] = (
            f"{ref['table']} -.- {ref['reference_table']}"
        )
    for c in connections:
        lines.append(c)
    return "\n".join(lines)


def mermaid(x):
    table = ""
    lines = ["flowchart LR"]
    for l in x.split("\n"):
        pattern = r'Table "public\.(\w+)"'
        for match in re.findall(pattern, l):
            if match != table:
                if table != "":
                    lines.append("end")
                table = match
                lines.append(f"subgraph {table}")

        pattern = r"(.*)\|(.*)\|(.*)\|(.*)\|(.*)"
        for match in re.findall(pattern, l):
            if match[0].strip() != "Column":
                # logging.info(match)
                lines.append(f"{table}.{match[0].strip()}")
    lines.append("end")
    pattern = r'TABLE "(\w+)" CONSTRAINT "(\w+)" FOREIGN KEY \((\w+)\) REFERENCES (\w+)\((\w+)\)'
    for match in re.findall(pattern, x):
        ref = {
            "table": match[0],
            "constraint": match[1],
            "foreign_key": match[2],
            "reference_table": match[3],
            "reference_column": match[4],
        }
        lines.append(
            f"{ref['table']}.{ref['foreign_key']} -.- {ref['reference_table']}.{ref['reference_column']}"
        )
    return "\n".join(lines)
