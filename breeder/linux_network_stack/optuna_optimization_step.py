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


# Godon Optuna Objective
import objective

# Optuna Framework
import optuna
from optuna.storages import InMemoryStorage
from optuna.integration import DaskStorage
from distributed import Client, wait

ARCHIVE_DB_USER = os.environ.get("ARCHIVE_DB_USER")
ARCHIVE_DB_PASSWORD = os.environ.get("ARCHIVE_DB_PASSWORD")
ARCHIVE_DB_HOSTNAME = os.environ.get("ARCHIVE_DB_HOSTNAME")
ARCHIVE_DB_PORT = os.environ.get("ARCHIVE_DB_PORT")
ARCHIVE_DB_DATABASE = os.environ.get("ARCHIVE_DB_DATABASE")

DASK_OPTUNA_SCHEDULER_URL = os.environ.get("DASK_OPTUNA_SCHEDULER_URL")

DLM_DB_USER = os.environ.get("DLM_DB_USER")
DLM_DB_PASSWORD = os.environ.get("DLM_DB_PASSWORD")
DLM_DB_HOST = os.environ.get("DLM_DB_HOST")
DLM_DB_DATABASE = os.environ.get("DLM_DB_DATABASE")
DLM_DB_CONNECTION = f"postgresql://{DLM_DB_USER}:{DLM_DB_PASSWORD}@{DLM_DB_HOST}/{DLM_DB_DATABASE}"


## TODO - Pass Breeer Config plus ID
## TODO - Pass DASK OPTUNA Entry Point
## TODO - Pass ARCHIVE_DB URL
def main(iteration: str):

            objective_kwargs = dict(archive_db_url=f'postgresql://{ARCHIVE_DB_USER}:{ARCHIVE_DB_PASSWORD}@{ARCHIVE_DB_HOSTNAME}:{ARCHIVE_DB_PORT}/{ARCHIVE_DB_DATABASE}',
                                    locking_db_url=DLM_DB_CONNECTION,
                                    run=run,
                                    identifier=identifier,
                                    breeder_id=config.get('uuid'),
                                    )

            __directions = list()

            for __objective in config.get('objectives'):
                direction = __objective.get('direction')
                __directions.append(direction)

            with Client(address=DASK_OPTUNA_SCHEDULER_URL) as client:
                # Create a study using Dask-compatible storage
                storage = DaskStorage(InMemoryStorage())
                study = optuna.create_study(directions=__directions, storage=storage)
                objective_wrapped = lambda trial: objective(trial, **objective_kwargs)
                # Optimize in parallel on your Dask cluster
                futures = [
                    client.submit(study.optimize, objective_wrapped, n_trials=10, pure=False)
                ]
                wait(futures, timeout=7200)

