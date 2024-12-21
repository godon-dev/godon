#
# Copyright (c) 2019 Matthias Tafelmeier.
#
# This file is part of godon
#
# godon is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# godon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this godon. If not, see <http://www.gnu.org/licenses/>.
#



def objective(trial,
              run=None,
              identifier=None,
              archive_db_url=None,
              locking_db_url=None,
              breeder_id=None):

    import pals
    import asyncio

    from sqlalchemy import create_engine
    from sqlalchemy import text

    logger = logging.getLogger('objective')
    logger.setLevel(logging.DEBUG)

    logger.debug('entering')

    archive_db_engine = create_engine(archive_db_url)

    # Compiling settings for effectuation
    settings = []
    setting_full = []
    for setting_name, setting_config in config.get('settings').get('sysctl').items():
        constraints = setting_config.get('constraints')
        step_width = setting_config.get('step')
        suggested_value = trial.suggest_int(setting_name, constraints.get('lower') , constraints.get('upper'), step_width)

        setting_full.append({ setting_name : suggested_value })

        if setting_name in ['net.ipv4.tcp_rmem', 'net.ipv4.tcp_wmem']:
            settings.append(f"sudo sysctl -w {setting_name}='4096 131072 {suggested_value}';")
        else:
            settings.append(f"sudo sysctl -w {setting_name}='{suggested_value}';")
    settings = '\n'.join(settings)
    setting_full = json.dumps(setting_full)

    is_setting_explored = False
    setting_id = hashlib.sha256(str.encode(settings)).hexdigest()[0:6]

    logger.debug('fetching setting data')

    breeder_table_name = f"{breeder_id}_{run}_{identifier}"
    query = f"SELECT * FROM {breeder_table_name} WHERE {breeder_table_name}.setting_id = '{setting_id}';"

    archive_db_data = archive_db_engine.execute(query).fetchall()

    if archive_db_data:
        logger.debug('setting already explored')
        is_setting_explored = True
        result_tuple = json.loads(archive_db_data[0])
        rtt = result_tuple[0]
        delivery_rate = result_tuple[1]

    # TODO - drop synchronisation via nats and call effectuation flow on wmill
    if not is_setting_explored:
        logger.warning('doing effectuation')
        is_setting_explored = True
        settings_data = dict(settings=settings)

        # get lock to gate other objective runs
        locker = pals.Locker('network_breeder_effectuation', locking_db_url)

        dlm_lock = locker.lock(f'{breeder_id}')

        if not dlm_lock.acquire(acquire_timeout=1200):
            task_logger.debug("Could not aquire lock for {breeder_id}")


        asyncio.run(send_msg_via_nats(subject=f'effectuation_{identifier}', data_dict=settings_data))

        logger.info('gathering recon')
        metric = json.loads(asyncio.run(receive_msg_via_nats(subject=f'recon_{identifier}')))


        # release lock to let other objective runs effectuation
        dlm_lock.release()

        metric_value = metric.get('metric')
        rtt = float(metric_value['tcp_rtt'])
        delivery_rate = float(metric_value['tcp_delivery_rate_bytes'])
        logger.info(f'metric received {metric_value}')

        setting_result = json.dumps([rtt, delivery_rate])

        query = f"INSERT INTO {breeder_table_name} VALUES ('{setting_id}', '{setting_full}', '{setting_result}');"
        archive_db_engine.execute(query)

        logger.warning('Result stored in Knowledge Archive')

    logger.warning('Done')

    return rtt, delivery_rate


