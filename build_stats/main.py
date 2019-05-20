import logging
from logging import config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

import asyncio
import click
import json
import os
import matplotlib.pyplot as plt
import sys
from .commons import JenkinsJob

@click.group()
def cli():
    pass

@cli.command()
@click.option('--auth', envvar='AUTH', help='<user>:<jenkins token> pair. Can also be passed with env var AUTH.')
@click.option('--output', type=click.Path(exists=True, file_okay=False), required=True, help='Download location for Jenkins jobs.')
@click.argument('job')
def download(auth, output, job):
    """Downloads the last 99 builds from Jenkins JOB."""
    user, password = os.environ['AUTH'].split(":")

    loop = asyncio.get_event_loop()
    j = JenkinsJob(job, user, password)
    build_details = loop.run_until_complete(j.download())

    # So far we are lazy and first download everything and save it then in a patch.
    for build in build_details:
        if build is not None:
            with open('{}/{}.json'.format(output, build['id']), 'w') as outfile:
                json.dump(build, outfile)

@cli.command()
@click.option('--job', type=click.Path(exists=True, file_okay=False), required=True, help='Location of Jenkins job builds.')
@click.option('--html/--no-html', default=False, help='Print stats as HTML.')
def analyze(job, html):
    """Analyzes all builds in job folder."""
    j = JenkinsJob.load(job)

    loop = asyncio.get_event_loop()
    tests = loop.run_until_complete(j.unique_fails())
    errors = loop.run_until_complete(j.unique_errors())
    if html:
        print(errors.to_html())
        print(tests.to_html())
    else:
        print(errors)
        print(tests)

@cli.command()
@click.option('--job', type=click.Path(exists=True, file_okay=False), required=True, help='Location of Jenkins job builds.')
@click.option('--output', type=click.Path(exists=False, dir_okay=False), required=True, help='Location of the plot.')
def timeline(job, output):
    """Plots a timeline of all builds in job folder and saves the result to output."""
    j = JenkinsJob.load(job)

    fail_statuses = ['FAILED', 'REGRESSION']
    loop = asyncio.get_event_loop()
    df = loop.run_until_complete(j.test_dataframe())

    ts = df.groupby(level=0).agg({'status': lambda x: x.isin(fail_statuses).any(), 'timestamp': 'max'})

    plt.figure(figsize=(20, 3)) 
    c = ts.status.map({True: 'xkcd:light red', False: 'xkcd:light blue'})
    plt.bar(x=ts.timestamp, height=1, width=0.01, color=c, align='edge')
    plt.xlim([ts.timestamp.min(), ts.timestamp.max()])
    plt.savefig(output, format='png')

if __name__ == '__main__':
    cli()
