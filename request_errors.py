
from flask import request, jsonify
from functools import wraps


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
