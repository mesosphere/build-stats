import logging
from logging import config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

import asyncio
import click
import datetime
import dominate
import dominate.tags as dt
import io
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

@cli.command()
@click.option('--job', '-j', multiple=True, type=click.Path(exists=True, file_okay=False), required=True, help='Location of Jenkins job builds.')
@click.argument('report', type=click.Path())
def report(job, report):
    """Generate a report.html with analysis and timelines from given jobs."""
    jobs = job

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    doc = dominate.document(title='Build Stats - {}'.format(today))
    with doc.head:
        dt.link(rel='stylesheet', href='https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/3.0.1/github-markdown.min.css')
        dt.meta(name='viewport', content='width=device-width, initial-scale=1')

    # Create <article>...</article> according to sindresorhus/github-markdown-css
    article = dt.article(cls='markdown-body')
    doc += article

    with article:
        dt.h1('Marathon Loop Build Stats ({})'.format(today))

    # Generate report for each job.
    for job in jobs:
        j = JenkinsJob.load(job)

        loop = asyncio.get_event_loop()
        tests = loop.run_until_complete(j.unique_fails()).to_html()
        errors = loop.run_until_complete(j.unique_errors()).to_html()

        f = io.BytesIO()
        fail_statuses = ['FAILED', 'REGRESSION']
        loop = asyncio.get_event_loop()
        df = loop.run_until_complete(j.test_dataframe())

        ts = df.groupby(level=0).agg({'status': lambda x: x.isin(fail_statuses).any(), 'timestamp': 'max'})

        plt.figure(figsize=(20, 3)) 
        c = ts.status.map({True: 'xkcd:light red', False: 'xkcd:light blue'})
        plt.bar(x=ts.timestamp, height=1, width=0.01, color=c, align='edge')
        plt.xlim([ts.timestamp.min(), ts.timestamp.max()])
        plt.savefig(f, format='svg')

        with article:
            dt.h2('Marathon {}'.format(job))
            dt.div(dominate.util.raw(errors))
            dt.div(dominate.util.raw(tests))
            dt.div(dominate.util.raw(f.getvalue().decode('utf-8')))

    with open(report, "w") as report_file:
        print(doc, file=report_file)

if __name__ == '__main__':
    cli()
