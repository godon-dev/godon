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

# Optuna Backend Communication Function Callback

class CommunicationCallback:
    def __init__(self):

        nats_service = dict(host=os.environ.get('GODON_NATS_SERVICE_HOST'),
                          port=os.environ.get('GODON_NATS_SERVICE_PORT'))

        self.nats_service_url = "nats://{host}:{port}".format(**nats_service)

    async def __communicate(self):
        return

    def __call__(self, study: optuna.study.Study, trial: optuna.trial.FrozenTrial) -> None:
        import asyncio

        asyncio.run(self.__communicate())

        return

# Optuna Backend Objective Function
def objective(trial,
              run=None,
              identifier=None,
              archive_db_url=None,
              locking_db_url=None,
              breeder_id=None):

    import pals
    import asyncio

    ## Compiling settings for effectuation
    def config_compile_settings(config=None):
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
        settings_full = json.dumps(setting_full)

        return (settings, settings_full)

    ## Effectuation Logic
    def perform_effectuation(breeder_id=None, identifier=None, settings=None, locking_db_url=None):
        logger.warning('doing effectuation')
        settings_data = dict(settings=settings)

        # get lock to gate other objective runs
        locker = pals.Locker('network_breeder_effectuation', locking_db_url)

        dlm_lock = locker.lock(f'{breeder_id}')

        if not dlm_lock.acquire(acquire_timeout=1200):
            task_logger.warning("Could not aquire lock for {breeder_id}")


        ## TODO - invoke
        asyncio.run(send_msg_via_nats(subject=f'effectuation_{identifier}', data_dict=settings_data))

        # TODO - drop synchronisation via nats and call effectuation flow on wmill
        logger.info('gathering recon')
        metric = json.loads(asyncio.run(receive_msg_via_nats(subject=f'recon_{identifier}')))


        # release lock to let other objective runs effectuation
        dlm_lock.release()

        metric_value = metric.get('metric')
        rtt = float(metric_value['tcp_rtt'])
        delivery_rate = float(metric_value['tcp_delivery_rate_bytes'])
        logger.info(f'metric received {metric_value}')

        setting_result = json.dumps([rtt, delivery_rate])

        return setting_result

    ## >> OBJECTIVE MAIN PATH << ##

    logger = logging.getLogger('objective')
    logger.setLevel(logging.DEBUG)

    logger.debug('entering')

    # Assemble Breeder Associated Archive DB Table Name
    breeder_table_name = f"{breeder_id}_{run_id}_{identifier}"

    setting_result = perform_effectuation(breeder_id=breeder_id,
                                          identifier=identifier,
                                          settings=settings,
                                          locking_db_url=locking_db_url)

    rtt = setting_result[0]
    delivery_rate = setting_result[1]

    logger.debug('exiting')

    return rtt, delivery_rate
