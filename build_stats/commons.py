import aiohttp
import asyncio
import json
import logging
import numpy
import os
import pandas
import requests

from collections import Counter

logger = logging.getLogger(__name__)

class JenkinsJob:
    
    def __init__(self, job, user, password, test_dataframe=None):
        self._job = job
        self._build_ids = list()
        self._user = user
        self._password = password
        self._auth = aiohttp.BasicAuth(user, password)

        if test_dataframe is None:
            self.__update_build_ids()
        
        self._test_cache = test_dataframe

    @classmethod
    def load(cls, location):
        build_details = list()
        for f in os.listdir(location):
            full_path = os.path.join(location, f)
            with open(full_path, 'r') as build_file:
                build_details.append(json.load(build_file))
   
        logger.info("Loaded %s tests from %s", len(build_details), location)

        test_dataframe = JenkinsJob.create_pandas(build_details)
        return cls(None, "unknown", "unknown", test_dataframe)
        
    def __update_build_ids(self):
        path = "{}/api/json?pretty=true&allBuilds=true".format(self._job)
        self._build_ids = [b['number']
                           for b
                           in requests.get(path, auth=(self._user, self._password)).json()['builds']][1:]
        logger.info('Found %d builds for %s', len(self._build_ids), self._job)
        
    async def grab_test(self, session, build_id):
        path = "{}/{}/testReport/api/json".format(self._job, build_id)
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

    async def download(self):
        logger.info('Downloading %d builds...', len(self._build_ids))
        build_details = await self.grab_tests(self._build_ids)
        logger.info('...done.')
        return build_details

    @staticmethod
    def create_pandas(build_details):
        def data_generator():
            for build in build_details:
                if build is not None:
                    for suite in build['suites']:
                        for case in suite['cases']:
                            yield (build['id'],
                                   case['className'],
                                   case['name'],
                                   case['status'],
                                   case['errorDetails'],
                                   numpy.datetime64(suite['timestamp']))

        columns = ['build_id', 'testsuite', 'testcase', 'status', 'error', 'timestamp']
        return pandas.DataFrame(data_generator(), columns=columns).set_index(['build_id', 'testsuite', 'testcase'])

    async def test_dataframe(self):
        if self._test_cache is not None:
            return self._test_cache

        build_details = await self.download()
        self._test_cache = create_pandas(build_details)
        return self._test_cache

    async def unique_fails(self):
        df = await self.test_dataframe()
        fail_statuses = ['FAILED', 'REGRESSION']
        return df[df.status.isin(fail_statuses)].drop(['timestamp'], axis=1).groupby(level=['testsuite', 'testcase']).count()

    async def unique_errors(self):
        df = await self.test_dataframe()
        fail_statuses = ['FAILED', 'REGRESSION']
        return df[df.status.isin(fail_statuses)].drop(['timestamp'], axis=1).groupby('error').count()
