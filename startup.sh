#!/bin/bash

flask db migrate
flask populate_db

flask run --host=0.0.0.0

