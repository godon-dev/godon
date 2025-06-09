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
# You should have received a copy of the GNU Affero General Public License
# along with this godon. If not, see <http://www.gnu.org/licenses/>.


## -- Purpose
## Communicator Perpectual Script Service
## It receives and processes Results from Optuna Optimizations
## via NATS (PUBSUB) and updates the cooperating metaheuristics
## state following certain communication policies.

import nats
import asyncio
import optuna
import os


NATS_SERVICE=dict(host=os.environ.get('GODON_NATS_SERVICE_HOST'),
                  port=os.environ.get('GODON_NATS_SERVICE_PORT'))


async def update_breeder_peers(peers=[], trial=None):
   return


async def message_handler(message):
    subject = message.subject
    reply = message.reply
    data = message.data.decode()


async def communication(nats_topic: str = None):

    nats_connection = await nats.connect("nats://{host}:{port}".format(**NATS_SERVICE))

    ## Time box the perpetual script as recommended by windmill
    timer = 0
    while true:

        ## End script
        if timer == 1000:
            break

        # Async subscriber via coroutine
        subscription = await nats_connection.subscribe(nats_topic, cb=message_handler)

        # Stop receiving after some messages
        await subscription.unsubscribe(limit=1000)

        timer += 1

    client.close()

    return


def main(nats_topic: str = "communication"):

    asyncio.run(communication(nats_topic=nats_topic))

    return
