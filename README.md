# Build Stats


## Installation

```
brew install pipenv
pipenv install
```

## Usage 

Python 3.6 is required to run the build stats commands. You can either use [poetry](https://poetry.eustace.io/)

```
mkdir loop
AUTH=<user>:<token> poetry run build_stats --output=loop <jenkins-job-url>
```

or build and use the Docker image

```
docker build -t buildstats .
docker run --env AUTH=<user>:<token> buildstats:latest python build_stats/main.py <jenkins-job-url>
```

For example, to fetch the stats for Marathon's system tests run

```
AUTH=<user>:<token> peotry run python build_stats/main.py --output=master.png \
    "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/system-integration-tests/job/marathon-si-dcos-open/job/master"
```

For mor details see `poetry run python build_stats/main.py --help`.
