
from .archive_db import archive_db
from .archive_db import ARCHIVE_DB_CONFIG
from .meta_data_db import queries
from .meta_data_db import META_DB_CONFIG

import datetime

def determine_config_shard(run_id=None,
                           target_id=None,
                           config=None,
                           targets_count=0,
                           parallel_runs_count=0):

    config_result = copy.deepcopy(config)
    settings_space = config_result.get('settings').get('sysctl')

    for setting in settings_space.items():
        upper = setting.get('constraints').get('upper')
        lower = setting.get('constraints').get('lower')

        delta = abs(upper - lower)

        shard_size = delta / targets_count * parallel_runs_count

        setting['constraints']['lower'] = lower + shard_size * (run_id + target_id)

    config_result['settings']['sysctl'] = settings_space

    return config_result




def main(request_data):

    # extract config from request
    breeder_config = request_data.get('breeder_config').get('breeder')
    breeder_name = breeder_config.get('name')
    parallel_runs = breeder_config.get('run').get('parallel')
    targets = breeder_config.get('effectuation').get('targets')
    consolidation_probability = breeder_config.get('cooperation').get('consolidation').get('probability')

    # generate breeder uuid and set in config
    uuid = uuid.uuid4()
    breeder_config.update(dict(uuid=uuid))

    ## create knowledge archive db relevant state

    # set dbname to work with to breeder_id
    db_config = ARCHIVE_DB_CONFIG.copy()
    db_config.update(dict(dbname="archive_db"))

    __query = archive.queries.create_breeder_table(table_name=uuid)
    archive.archive_db.execute(db_info=db_config, query=__query)

    for target in targets:
        hash_suffix = hashlib.sha256(str.encode(target.get('address'))).hexdigest()[0:6]
        for run_id in range(0, parallel_runs):
            breeder_id = f'{uuid}_{run_id}_{hash_suffix}'

            __query = archive.queries.create_breeder_table(table_name=breeder_id)
            archive.archive_db.execute(db_info=db_config, query=__query)

            __query = archive.queries.create_procedure(procedure_name=f'{breeder_id}_procedure',
                                                       probability=consolidation_probability,
                                                       source_table_name=breeder_id,
                                                       target_table_name=breeder_name)
            archive.archive_db.execute(db_info=db_config, query=__query)

            __query = archive.queries.create_trigger(trigger_name=f'{breeder_id}_trigger',
                                                     table_name=breeder_id,
                                                     procedure_name=f'{breeder_id}_procedure')
            archive.archive_db.execute(db_info=db_config, query=__query)

    ## create and fill breeder meta data db
    db_config = META_DB_CONFIG.copy()
    db_config.update(dict(dbname='meta_data'))
    db_table_name = 'breeder_meta_data'

    __query = meta_data.queries.create_meta_breeder_table(table_name=db_table_name)
    archive.archive_db.execute(db_info=db_config, query=__query)

    __query = meta_data.queries.insert_breeder_meta(table_name=db_table_name,
                                                  breeder_id=uuid,
                                                  creation_ts=datetime.datetime.now(),
                                                  meta_state=breeder_config)
    archive.archive_db.execute(db_info=db_config, query=__query)

    # TODO - adjust breeder flows initialization to wmill way

#    for target in targets:
#        hash_suffix = hashlib.sha256(str.encode(target.get('address'))).hexdigest()[0:6]
#
#        for run_id in range(0, parallel_runs):
#            dag_id = f'{dag_name}_{run_id}'
#            if not is_cooperative:
#                config = determine_config_shard()
#            globals()[f'{dag_id}_optimization_{hash_suffix}'] = create_optimization_dag(f'{dag_id}_optimization_{hash_suffix}', config, run_id, hash_suffix)
#            globals()[f'{dag_id}_target_{hash_suffix}'] = create_target_interaction_dag(f'{dag_id}_target_interaction_{hash_suffix}', config, target, hash_suffix)
#
#        target_id += 1


    return { "result": "SUCCESS", "breeder_id": uuid }

