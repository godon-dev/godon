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



def main():

## TODO - Decide on which effectuator and apply it here.

#       _ssh_hook = SSHHook(
#           remote_host=target.get('address'),
#           username=target.get('user'),
#           key_file=target.get('key_file'),
#           conn_timeout=30,
#           keepalive_interval=10
#       )

#       effectuation_step = SSHOperator(
#           ssh_hook=_ssh_hook,
#           task_id='effectuation',
#           conn_timeout=30,
#           command="""
#                   {{ ti.xcom_pull(task_ids='pull_optimization_step') }}
#                   """,
#           dag=interaction_dag,
#       )

    return True
