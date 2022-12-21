#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys

from datetime import date, datetime, timedelta

sys.path.insert(0, '../')

from flask import (Flask, jsonify, request)
from flask_moment import Moment

from models import *


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

app.config.from_pyfile('config.py')

db.init_app(app)

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return jsonify({
        # 't1': t1,
        # 't2': t2
        # 'tickets of user 1': [ticket.format() for ticket in User.query.get(1).tickets],
        # 'users that user 1 follows (user 1 followings)': [User.query.get(uf.followed).format() for uf in User.query.get(1).followings],
        # 'users that follow user 1 (user 1 followers)': [User.query.get(uf.follower).format() for uf in User.query.get(1).followers],
        'avengers': [movie.format() for movie in movies]
    }), 200
 

@app.route('/avatars', methods=['GET'])
def get_avatars():
    avatars = []
    for i in range(1, 10):
        avatars.append({
            'id': i,
            'url': f"{PROFILE_PICTURE_BASE_URL}avatars/{i}.jpg"
        })
        
    return jsonify({
        'success': True,
        'avatars': avatars
    }), 200

    
@app.route('/init')
def init():
    db.engine.execute("DROP SCHEMA public CASCADE;")
    db.engine.execute("CREATE SCHEMA public;")

    db.create_all(app=app)
    
    return jsonify({
        'success': True
    }), 200
    

@app.route('/confirm_coupon_purchase', methods=['POST'])
def confirm_coupon_purchase():
    body = request.get_json()
    
    order_id = body['obj']['order']['id']
    transaction_id = body['obj']['id']
    
    return jsonify({
        'success': True
    }), 200
    
#----------------------------------------------------------------------------#
# Error Handlers.
#----------------------------------------------------------------------------#

@app.errorhandler(400)
def error_400(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': error.description
    }), 400

@app.errorhandler(401)
def error_400(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': error.description
    }), 401
    
@app.errorhandler(403)
def error_400(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': error.description
    }), 403

@app.errorhandler(404)
def error_404(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': error.description
    }), 404
    
@app.errorhandler(409)
def error_409(error):
    return jsonify({
        'success': False,
        'error': 409,
        'message': error.description
    }), 409
    
@app.errorhandler(500)
def error_500(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': error.description
    }), 500
    
@app.errorhandler(502)
def error_500(error):
    return jsonify({
        'success': False,
        'error': 502,
        'message': error.description
    }), 502


if __name__ == '__main__':
    app.run(debug=False)