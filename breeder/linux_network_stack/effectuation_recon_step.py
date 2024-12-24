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



from prometheus_api_client import PrometheusConnect, MetricsList, Metric
from prometheus_api_client.utils import parse_datetime

import urllib3


def main(prometheus_url=None):

    task_logger.debug("Entering")

    prom_conn = PrometheusConnect(url=PROMETHEUS_URL,
                                  retry=urllib3.util.retry.Retry(total=3,
                                                                 raise_on_status=True,
                                                                 backoff_factor=0.5),
                                  disable_ssl=True)

    metric_data = dict()
    for objective in config.get('objectives'):
        recon_service_type = objective.get('reconaissance').get('service')

        if recon_service_type == 'prometheus':
            recon_query = objective.get('reconaissance').get('query')
            query_name = objective.get('name')
            query_result = prom_conn.custom_query(recon_query)
            if query_result.get('resultType') != 'scalar':
                raise Exception("Custom Query must be of result type scalar.")
            # Example format of result processed
            #   "data": {
            #       "resultType": "scalar",
            #       "result": [
            #         1703619892.31, << TS
            #         "0.401370548"  << Value
            #       ]
            #     }
            value = metric_value.get('result')[1]

            if value == "NaN":
                raise Exception("Scalar reduction of custom query probably ailing, only returning NaN.")

            metric_data[query_name] = value
        else:
            raise Exception("Reconnaisance service type {recon_service_type} not supported yet.")

    task_logger.debug("Done")
