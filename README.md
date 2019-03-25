# Build Stats


## Installation

```
brew install pipenv
pipenv install
```

## Usage 

Run the main method with

```
AUTH=<user>:<token> pipenv run main.py --output=graph.png <jenkins-job-url>
```

For example, to fetch the stats for Marathon's system tests run

```
AUTH=<user>:<token> pipenv run main.py --output=master.png \
    "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/system-integration-tests/job/marathon-si-dcos-open/job/master"
```

For mor details see `pipenv run main.pu --help`.
