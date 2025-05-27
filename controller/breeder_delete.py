
from .archive_db import archive_db
from .archive_db import queries as archive_db_queries
from .archive_db import ARCHIVE_DB_CONFIG
from .meta_data_db import queries as meta_data_db_queries
from .meta_data_db import META_DB_CONFIG


def main(breeder_id=None):

    # extract config from request_data
    __uuid_common_name = "_" + breeder_id.replace('-', '_')

    ## cleanup knowledge archive db relevant state
    db_config = ARCHIVE_DB_CONFIG.copy()
    db_config.update(dict(dbname="archive_db"))

    __query = archive_db_queries.fetch_tables(uuid=__uuid_common_name)
    archive_tables = archive_db.execute(db_info=db_config, query=__query, with_result=True)

    for table_name in archive_tables:
        __query = archive_db_queries.delete_breeder_table(table_name=table_name[0])
        archive_db.execute(db_info=db_config, query=__query)

    __query = archive_db_queries.fetch_procedures(breeder_id=__uuid_common_name)
    procedures = archive_db.execute(db_info=db_config, query=__query, with_result=True)

    for procedure_name in procedures:
        logging.error(type(procedure_name))
        logging.error(procedure_name)
        __query = archive_db_queries.delete_procedure(procedure_name=procedure_name[0])
        archive_db.execute(db_info=db_config, query=__query)

    ## cleanup breeder meta data db state
    db_config = META_DB_CONFIG.copy()
    db_config.update(dict(dbname='meta_data'))
    db_table_name = 'breeder_meta_data'

    __query = meta_data_db_queries.remove_breeder_meta(table_name=db_table_name,
                                                       breeder_id=breeder_id)
    archive_db.execute(db_info=db_config, query=__query)

    return { "result": "SUCCESS" }

