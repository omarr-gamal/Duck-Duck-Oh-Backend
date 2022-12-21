import re

from flask import request, jsonify, abort
from functools import wraps


def validate_date(date):
    if date is not None and not check_date_format(date):
        abort(400, 'Invalid date format. Format must match yyyy-mm-dd')

# matches 2020-01-23
def check_date_format(input):
    pattern = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$")
    return bool(pattern.match(input))


def requires_body(fields=''):
    def requires_body_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            body = request.get_json()

            if not body:
                return jsonify({
                    'success': False,
                    'error': 400,
                    'message': 'No request body found.'
                }), 400


            # for patch requests, there should be a request body
            # so the decorator should be used like: @requires_body('')
            if fields == '':
                return f(*args, **kwargs)

            body_fields = fields.split(' ')          

            for field in body_fields:
                if field not in body:
                    return jsonify({
                        'success': False,
                        'error': 400,
                        'message': 'Missing field: {}'.format(field)
                    }), 400

            return f(*args, **kwargs)

        return wrapper
    return requires_body_decorator


def requires_args(arguments):
    def requires_args_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            arg_fields = arguments.split(' ')          

            for field in arg_fields:
                if field not in request.args:
                    return jsonify({
                        'success': False,
                        'error': 400,
                        'message': 'Missing argument: {}'.format(field)
                    }), 400

            return f(*args, **kwargs)

        return wrapper
    return requires_args_decorator
