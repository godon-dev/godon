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
    def __init__(self, archive_db_storage : str = None, consolidation_probability: float = None):

        self.storage = archive_db_storage
        self.com_probability = consolidation_probability

        return

    def __communicate(self, study: optuna.study.Study, trial: optuna.trial.FrozenTrial) -> None:

        for __study_name in study.get_all_study_names(storage=self.storage):
            cooperating_study = optuna.load_study(study_name=__study_name, storage=self.storage)

            cooperating_study.add_trial(trial)

        return


    def __call__(self, study: optuna.study.Study, trial: optuna.trial.FrozenTrial) -> None:
        import random

        logger = logging.getLogger('communication-cb')
        logger.setLevel(logging.DEBUG)

        random_value = random.random()

        if self.com_probability > random_value:
            self.__communicate()

        return


class Objective:
    def __init__(self, config: dict):

        # Optuna Backend Objective Function
#        def objective(trial,
#              run=None,
#              identifier=None,
#              archive_db_url=None,
#              locking_db_url=None,
#              breeder_id=None):

        self.config = config

        return

    ## Compiling settings for effectuation
    def __config_compile_settings(self):
            settings = []
            setting_full = []
            for setting_name, setting_config in self.config.get('settings').get('sysctl').items():
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
    def __perform_effectuation(self, breeder_id=None, identifier=None, settings=None, locking_db_url=None):
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


    def __call__(self, trial):
        import pals
        import asyncio


        ## >> OBJECTIVE MAIN PATH << ##

        logger = logging.getLogger('objective')
        logger.setLevel(logging.DEBUG)

        logger.debug('entering')

        # Assemble Breeder Associated Archive DB Table Name
        breeder_table_name = f"{breeder_id}_{run_id}_{identifier}"


        settings = self.__config_compile_settings()

        setting_result = self.__perform_effectuation(breeder_id=breeder_id,
                                                     identifier=identifier,
                                                     settings=settings,
                                                     locking_db_url=locking_db_url)

        rtt = setting_result[0]
        delivery_rate = setting_result[1]

        logger.debug('exiting')

        return rtt, delivery_rate

