#!/usr/bin/env bash

rm -r loop-* permissive open strict 1.*.png || true

mkdir loop-1.5 
poetry run build-stats download --output=loop-1.5 "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/marathon-sandbox/job/marathon-loop-1.5/"
poetry run build-stats analyze --job=loop-1.5 --html
poetry run build-stats timeline --job=loop-1.5 --output=1.5.png

mkdir loop-1.6 
poetry run build-stats download --output=loop-1.6 "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/marathon-sandbox/job/marathon-loop-1.6/"
poetry run build-stats analyze --job=loop-1.6 --html
poetry run build-stats timeline --job=loop-1.6 --output=1.6.png

mkdir loop-1.7 
poetry run build-stats download --output=loop-1.7 "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/marathon-sandbox/job/marathon-loop-1.7/"
poetry run build-stats analyze --job=loop-1.7 --html
poetry run build-stats timeline --job=loop-1.7 --output=1.7.png

mkdir loop-master
poetry run build-stats download --output=loop-master "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/marathon-sandbox/job/marathon-loop-master/"
poetry run build-stats analyze --job=loop-master --html
poetry run build-stats timeline --job=loop-master --output=master.png

mkdir open 
poetry run build-stats download --output=open "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/system-integration-tests/job/marathon-si-dcos-open/job/master"
poetry run build-stats analyze --job=open --html

mkdir permissive 
poetry run build-stats download --output=permissive "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/system-integration-tests/job/marathon-si-dcos-permissive/job/master"
poetry run build-stats analyze --job=permissive --html

mkdir strict 
poetry run build-stats download --output=strict "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/system-integration-tests/job/marathon-si-dcos-strict/job/master"
poetry run build-stats analyze --job=strict --html
