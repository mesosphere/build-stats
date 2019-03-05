import logging
from logging import config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

import asyncio
import os
import sys
from commons import JenkinsJob
from IPython.display import HTML, display

async def main(job_name):
    user, password = os.environ['AUTH'].split(":")
    job = JenkinsJob("jenkins.mesosphere.com/service/jenkins/view/Marathon/job/", job_name, user, password)
    tests = await job.unique_fails()
    print(tests)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    job_name =  sys.argv[1] 
    loop.run_until_complete(main(job_name))
