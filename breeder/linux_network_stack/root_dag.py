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


from datetime import timedelta

import random
import logging
import json
import copy
import hashlib
import os




task_logger = logging.getLogger("airflow.task")
task_logger.setLevel(logging.DEBUG)

###

config = {{ breeder }}

parallel_runs = config.get('run').get('parallel')
targets = config.get('effectuation').get('targets')
dag_name = config.get('uuid')
is_cooperative = config.get('cooperation').get('active')

target_id = 0

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


for target in targets:
    hash_suffix = hashlib.sha256(str.encode(target.get('address'))).hexdigest()[0:6]

    for run_id in range(0, parallel_runs):
        dag_id = f'{dag_name}_{run_id}'
        if not is_cooperative:
            config = determine_config_shard()
        globals()[f'{dag_id}_optimization_{hash_suffix}'] = create_optimization_dag(f'{dag_id}_optimization_{hash_suffix}', config, run_id, hash_suffix)
        globals()[f'{dag_id}_target_{hash_suffix}'] = create_target_interaction_dag(f'{dag_id}_target_interaction_{hash_suffix}', config, target, hash_suffix)

    target_id += 1
