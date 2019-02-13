import aiohttp
import asyncio
import logging
import os
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
        self._failed_test_cases_cache = None
        
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
                return await resp.json()
            except:
                logger.exception('Could not fetch build %s', build_id)
                return None
            
    async def grab_tests(self, build_ids):
        async with aiohttp.ClientSession() as session:
            build_details = [self.grab_test(session, build_id) for build_id in build_ids]
            return await asyncio.gather(*build_details)
        
    async def failed_test_cases(self):
        if self._failed_test_cases_cache is None:
            logger.info('Downloading %d builds...', len(self._build_ids))
            build_details = await self.grab_tests(self._build_ids)
            logger.info('...done.')
        
            builds = (build for build in build_details if build is not None)
            suites = (suite for build in builds for suite in build['suites'])
            cases = (case for suite in suites for case in suite['cases'])
            self._failed_test_cases_cache = [case for case in cases
                                             if case['status'] == 'FAILED' or case['status'] == 'REGRESSION']

        return self._failed_test_cases_cache
    
    async def unique_errors(self):
        errors = (case['errorDetails'] for case in await self.failed_test_cases())
        return Counter(errors)
    
    async def unique_errors_table(self, tablefmt):
        errors = await self.unique_errors()
        return tabulate(errors.items(), headers=['Unique Error', 'Count'], tablefmt=tablefmt)
            
    async def names(self):
        names = ('{}:{}'.format(case['className'], case['name']) for case in await self.failed_test_cases())
        return Counter(names)
        
    async def names_table(self, tablefmt):
        names = await self.names()
        return tabulate(names.items(), headers=['Test Case', 'Count'], tablefmt=tablefmt)

