import logging
from logging import config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

import asyncio
import click
import os
import matplotlib.pyplot as plt
import sys
from commons import JenkinsJob

async def plot(job, output):
    fail_statuses = ['FAILED', 'REGRESSION']
    df = await job.test_dataframe()
    ts = df.groupby(level=0).agg({'status': lambda x: x.isin(fail_statuses).any(), 'timestamp': 'max'})

    plt.figure(figsize=(20, 3)) 
    c = ts.status.map({True: 'xkcd:light red', False: 'xkcd:light blue'})
    plt.bar(x=ts.timestamp, height=1, width=0.01, color=c, align='edge')
    plt.xlim([ts.timestamp.min(), ts.timestamp.max()])
    plt.savefig(output, format='png')

async def analyze(user, password, job_name, output):
    job = JenkinsJob(job_name, user, password)
    tests = await job.unique_fails()
    print(tests)
    errors = await job.unique_errors()
    print(errors)
    await plot(job, output)

@click.command()
@click.option('--auth', envvar='AUTH', help='<user>:<jenkins token> pair. Can also be passed with env var AUTH.')
@click.option('--output', type=click.File('wb'), help='Location for graph PNG file.')
@click.argument('job')
def main(auth, output, job):
    """Analyzes the last 99 builds from Jenkins JOB."""
    user, password = os.environ['AUTH'].split(":")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(analyze(user, password, job, output))

if __name__ == '__main__':
    main()
