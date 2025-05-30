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

from .archive_db import ARCHIVE_DB_CONFIG

# Godon Optuna Objective
import objective

# Optuna Framework
import optuna
from optuna.storages import InMemoryStorage
from optuna.integration import DaskStorage
from distributed import Client, wait

DASK_OPTUNA_SCHEDULER = dict(host=os.environ.get("GODON_DASK_SCHEDULER_SERVICE_HOST"),
                             port=os.environ.get("GODON_DASK_SCHEDULER_SERVICE_PORT"))

GODON_LOCKING_DB = dict(user=locking,
                        password=locking,
                        host=os.environ.get("GODON_LOCKING_DB_SERVICE_HOST"),
                        port=os.environ.get("GODON_LOCKING_DB_SERVICE_PORT"),
                        database=distributed_locking)

GODON_LOCKING_DB_CONNECTION_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}".format(**GODON_LOCKING_DB)


## TODO - Pass Breeer Config plus ID
## TODO - Pass ARCHIVE_DB URL
def main(config=None):

            archive_db_database = config.get('breeder_database')

            ## TODO - rework objective interface - use more sys or usr attrs of study
            objective_kwargs = dict(archive_db_url=None,
                                    locking_db_url=GODON_LOCKING_DB_CONNECTION_URL,
                                    run=run,
                                    identifier=identifier,
                                    breeder_id=config.get('uuid'),
                                    )

            __directions = list()

            for __objective in config.get('objectives'):
                direction = __objective.get('direction')
                __directions.append(direction)

            with Client(address="{host}:{port}".format(**DASK_OPTUNA_SCHEDULER)) as client:
                # Create a study using Dask-compatible storage
                archive_db_url = "postgresql://{user}:{password}@{host}:{port}".format(**ARCHIVE_DB_CONFIG) + archive_db_database

                rdb_storage = optuna.storages.RDBStorage(
                        url=archive_db_url
                        )

                storage = DaskStorage(rdb_storage)

                study = optuna.create_study(directions=__directions, storage=storage)
                objective_wrapped = lambda trial: objective(trial, **objective_kwargs)
                # Optimize in parallel on your Dask cluster
                futures = [
                    client.submit(study.optimize, objective_wrapped, n_trials=10, pure=False)
                ]
                wait(futures, timeout=7200)

