import aiohttp
import asyncio
import logging
import os
import pandas
import requests

from collections import Counter
from tabulate import tabulate

logger = logging.getLogger(__name__)

class JenkinsJob:
    
    def __init__(self, base, job, user, password):
        self._base = base
        self._job = job
        self._build_ids = list()
        self._user = user
        self._password = password
        self._auth = aiohttp.BasicAuth(user, password)
        self.__update_build_ids()
        
        # TODO(karsten): Investigate lru_cache
        self._test_cache = None
        
    def __update_build_ids(self):
        path = "https://{}/{}/api/json?pretty=true&allBuilds=true".format(self._base, self._job)
        self._build_ids = [b['number']
                           for b
                           in requests.get(path, auth=(self._user, self._password)).json()['builds']][1:]
        logger.info('Found %d builds for %s', len(self._build_ids), self._job)
        
    async def grab_test(self, session, build_id):
        path = "https://{}/{}/{}/testReport/api/json".format(self._base, self._job, build_id)
        # logger.debug('Fetching test %s', path)
        async with session.get(path, auth=self._auth) as resp:
            try:
                resp.raise_for_status()
                build = await resp.json()
                build['id'] = build_id
                return build
            except:
                logger.exception('Could not fetch build %s', build_id)
                return None
            
    async def grab_tests(self, build_ids):
        async with aiohttp.ClientSession() as session:
            build_details = [self.grab_test(session, build_id) for build_id in build_ids]
            return await asyncio.gather(*build_details)

    async def test_dataframe(self):
        if self._test_cache is not None:
            return self._test_cache

        logger.info('Downloading %d builds...', len(self._build_ids))
        build_details = await self.grab_tests(self._build_ids)
        logger.info('...done.')

        def data_generator():
            for build in build_details:
                if build is not None:
                    for suite in build['suites']:
                        for case in suite['cases']:
                            yield (build['id'], case['className'], case['name'], case['status'], case['errorDetails'])

        self._test_cache = pandas.DataFrame(data_generator(), columns=['build_id', 'testsuite', 'testcase', 'status', 'error'])
            .set_index(['build_id', 'testsuite', 'testcase'])
        return self._test_cache

    async def unique_fails(self):
        df = await self.test_dataframe()
        fail_statuses = ['FAILED', 'REGRESSION']
        return df[df.status.isin(fail_statuses)].groupby(level=['testsuite', 'testcase']).count()

    async def unique_errors(self):
        df = await self.test_dataframe()
        fail_statuses = ['FAILED', 'REGRESSION']
        return df[df.status.isin(fail_statuses)].groupby('error').count()
