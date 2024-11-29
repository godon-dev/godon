
from .archive_db import archive_db
from .archive_db import ARCHIVE_DB_CONFIG
from .meta_data_db import queries
from .meta_data_db import META_DB_CONFIG


def main(request_data):

    # extract config from request_data
    breeder_id = request_data.get("breeder_id")

    ## cleanup knowledge archive db relevant state

    # set dbname to work with to breeder_id
    db_config = ARCHIVE_DB_CONFIG.copy()
    db_config.update(dict(dbname="archive_db"))

    __query = archive.queries.delete_breeder_table(table_name=breeder_id)
    archive.archive_db.execute(db_info=db_config, query=__query)

    __query = archive.queries.fetch_procedures(breeder_id=breeder_id)
    procedures = archive.archive_db.execute(db_info=db_config, query=__query, with_result=True)

    for procedure_name in procedures:
        logging.error(type(procedure_name))
        logging.error(procedure_name)
        __query = archive.queries.delete_procedure(procedure_name=procedure_name[0])
        archive.archive_db.execute(db_info=db_config, query=__query)

    __query = archive.queries.fetch_tables(breeder_id=breeder_id)
    archive_tables = archive.archive_db.execute(db_info=db_config, query=__query, with_result=True)

    for table_name in archive_tables:
        logging.error(table_name)
        __query = archive.queries.delete_breeder_table(table_name=table_name[0])
        archive.archive_db.execute(db_info=db_config, query=__query)


    ## cleanup breeder meta data db state
    db_config = META_DB_CONFIG.copy()
    db_config.update(dict(dbname='meta_data'))
    db_table_name = 'breeder_meta_data'

    __query = meta_data.queries.remove_breeder_meta(table_name=db_table_name,
                                                    breeder_id=breeder_id)
    archive.archive_db.execute(db_info=db_config, query=__query)

    return { "result": "SUCCESS" }
