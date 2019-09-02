#!/usr/bin/env bash
set -x +e -o pipefail

rm -r loop-* permissive open strict 1.*.png || true

mkdir loop-1.6 
poetry run build-stats download --output=loop-1.6 "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/marathon-sandbox/job/marathon-loop-1.6/"

mkdir loop-1.7 
poetry run build-stats download --output=loop-1.7 "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/marathon-sandbox/job/marathon-loop-1.7/"

mkdir loop-1.8 
poetry run build-stats download --output=loop-1.8 "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/marathon-sandbox/job/marathon-loop-1.8/"

mkdir loop-master
poetry run build-stats download --output=loop-master "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/marathon-sandbox/job/marathon-loop-master/"

poetry run build-stats report -j loop-1.6 -j loop-1.7 -j loop-1.8 -j loop-master integration.html

mkdir open 
poetry run build-stats download --output=open "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/system-integration-tests/job/marathon-si-dcos-open/job/master"
poetry run build-stats analyze --job=open --html

mkdir permissive 
poetry run build-stats download --output=permissive "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/system-integration-tests/job/marathon-si-dcos-permissive/job/master"
poetry run build-stats analyze --job=permissive --html

mkdir strict 
poetry run build-stats download --output=strict "https://jenkins.mesosphere.com/service/jenkins/view/Marathon/job/system-integration-tests/job/marathon-si-dcos-strict/job/master"
poetry run build-stats analyze --job=strict --html
