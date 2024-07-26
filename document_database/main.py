from .. import logging
from .. import database
from ..files import write
from ..files import read
import json
database_credentials = json.loads(read("/database.json"))
url = database.get_connection_url(
    user=database_credentials['user'],
    password=database_credentials['password'],
    host=database_credentials['host'],
    port=database_credentials['port'],
    database=database_credentials['database'],
    socket=database_credentials['socket'],
)
str_ = database.description(url)
write(
    "/destination/database.txt",
    str_
)
str_ = database.mermaid(read("/destination/database.txt"))
write(
    "/destination/database.mmd",
    str_
)
str_ = database.mermaid_simple(read("/destination/database.txt"))
write(
    "/destination/database_simple.mmd",
    str_
)