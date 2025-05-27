
from .archive_db import archive_db
from .meta_data_db import queries
from .meta_data_db import META_DB_CONFIG

import os
from dateutil.parser import parse

def main(request_data):

    ## fetch breeder meta data list
    db_config = META_DB_CONFIG.copy()
    db_config.update(dict(dbname='meta_data'))
    db_table_name = 'breeder_meta_data'
    configured_breeders = None

    __query = queries.fetch_breeders_list(table_name=db_table_name)
    breeder_meta_data_list = archive_db.execute(db_info=db_config, query=__query, with_result=True)

    if breeder_meta_data_list:
    # preformat timestamp to be stringifyable
        configured_breeders = [(breeder_row[0],breeder_row[1], parse(str(breeder_row[2])).isoformat()) for breeder_row in breeder_meta_data_list]

    result_content = configured_breeders if configured_breeders else list()

    return { "result": "SUCCESS",
             "breeders": configured_breeders }
