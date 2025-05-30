
from .archive_db import archive_db
from .archive_db import queries as archive_db_queries
from .archive_db import ARCHIVE_DB_CONFIG
from .meta_data_db import queries as meta_data_db_queries
from .meta_data_db import META_DB_CONFIG

import datetime
import uuid
import hashlib
import copy

def determine_config_shard(run_id=None,
                           target_id=None,
                           targets_count=None,
                           config=None,
                           parallel_runs_count=0):

    config_result = copy.deepcopy(config)
    settings_space = config_result.get('settings').get('sysctl')

    for setting in settings_space.items():
        upper = setting[1].get('constraints').get('upper')
        lower = setting[1].get('constraints').get('lower')

        delta = abs(upper - lower)

        shard_size = delta / targets_count * parallel_runs_count
        offset = (run_id + target_id)

        new_lower = int(lower + shard_size * offset)
        new_upper = int(new_lower + shard_size)

        setting[1]['constraints']['lower'] = new_lower
        setting[1]['constraints']['upper'] = new_upper

    config_result['settings']['sysctl'] = settings_space

    return config_result

def start_optimization_flow(flow_id, config):
    print("starting flow with config")
    print(config)
    return flow_id, config

def main(breeder_config=None):

    # extract config from request
    breeder_config = breeder_config.get('breeder')
    breeder_name = breeder_config.get('name')
    parallel_runs = breeder_config.get('run').get('parallel')
    targets = breeder_config.get('effectuation').get('targets')
    targets_count = len(targets)
    is_cooperative = breeder_config.get('cooperation').get('active')
    consolidation_probability = breeder_config.get('cooperation').get('consolidation').get('probability')

    # generate breeder uuid and set in config
    __uuid = str(uuid.uuid4())
    breeder_config.update(dict(uuid=__uuid))

    ## create knowledge archive db relevant state

    # set dbname to work with to breeder_id
    db_config = ARCHIVE_DB_CONFIG.copy()
    db_config.update(dict(dbname="archive_db"))


    __uuid_common_name = "breeder_" + __uuid.replace('-', '_')
    breeder_id = f'{__uuid_common_name}'

    # define per breeder database for optimization backend rdb storage
    __query = archive_db_queries.create_database(breeder_id=breeder_id)
    archive_db.execute(db_info=db_config, query=__query)

    ## create and fill breeder meta data db
    db_config = META_DB_CONFIG.copy()
    db_config.update(dict(dbname='meta_data'))
    db_table_name = 'breeder_meta_data'

    __query = meta_data_db_queries.create_meta_breeder_table(table_name=db_table_name)
    archive_db.execute(db_info=db_config, query=__query)

    __query = meta_data_db_queries.insert_breeder_meta(table_name=db_table_name,
                                                       breeder_id=__uuid,
                                                       creation_ts=datetime.datetime.now(),
                                                       meta_state=breeder_config)
    archive_db.execute(db_info=db_config, query=__query)

    target_count = 0
    for target in targets:
        hash_suffix = hashlib.sha256(str.encode(target.get('address'))).hexdigest()[0:6]

        for run_id in range(0, parallel_runs):
            config = breeder_config
            flow_id = f'{breeder_name}_{run_id}'
            if not is_cooperative:
                config = determine_config_shard(run_id=run_id,
                                                target_id=target_count,
                                                targets_count=targets_count,
                                                config=breeder_config,
                                                parallel_runs_count=parallel_runs)
            start_optimization_flow(flow_id, config)

        target_count += 1

    return { "result": "SUCCESS", "breeder_id": __uuid }
