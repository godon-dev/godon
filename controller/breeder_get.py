
from .archive_db import archive_db
from .meta_data_db import queries
from .meta_data_db import META_DB_CONFIG

import json

def main(request_data):

    ## fetch breeder meta data
    db_config = META_DB_CONFIG.copy()
    db_config.update(dict(dbname='meta_data'))
    db_table_name = 'breeder_meta_data'

    __query = meta_data.queries.fetch_meta_data(table_name=db_table_name, breeder_id=breeder_uuid)
    breeder_meta_data = archive.archive_db.execute(db_info=db_config, query=__query, with_result=True)

    return {
            "result": "SUCCESS",
             "breeder_data": json.dumps(dict(creation_timestamp=breeder_meta_data_row[0].isoformat(),
                                             breeder_definition=breeder_meta_data_row[1]))
             }
