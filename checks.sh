#!/usr/bin/env bash

echo "####### FLAKE8 #######"
flake8 --extend-ignore=E501 main/
echo "####### PYLINT #######"
pylint --load-plugins pylint_django --errors-only --rcfile=pylintrc main/
