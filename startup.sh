#!/bin/bash

export FLASK_APP=wsgi.py

flask db upgrade
flask populate_db

flask run --host=0.0.0.0
