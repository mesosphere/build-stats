import json
import os
from datadog import initialize, api
from datetime import datetime, timedelta

api_key = os.environ['DATADOG_API_KEY']
application_key = os.environ['DATADOG_APPLICATION_KEY']

def graph_def(job):
    definition = {"viz": "timeseries",
                  "requests": [
                      {"q": f"avg:marathon.build.marathon_loop_{job}.success{{*}}.as_count()",
                       "type": "bars",
                       "style": { "palette": "green", "type": "solid", "width": "normal"},
                       "aggregator": "avg",
                       "conditional_formats": []
                      },
                      {"q": f"avg:marathon.build.marathon_loop_{job}.failure{{*}}.as_count()",
                       "type": "bars",
                       "style": {"palette": "red","type": "solid","width": "normal"}
                      }
                  ],
                  "autoscale": True
                 }
    return json.dumps(definition)

def build_graph(job):
    initialize(api_key=api_key, app_key=application_key)

    end = datetime.now() 
    start = end - timedelta(days=2)
    return api.Graph.create(
        graph_def=graph_def(job),
        start=int(start.timestamp()),
        end=int(end.timestamp()),
        title='Marathon Master'
    )
