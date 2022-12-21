#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys

from datetime import date, datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from project.request_errors import requires_body
sys.path.insert(0, '../')

from flask import (Flask, jsonify, request)
from flask_moment import Moment

from project.config import SQLALCHEMY_DATABASE_URI

from project.models import *
from project.coupons.utils import invalidate_coupon_purchase


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

app.config.from_pyfile('config.py')

db.init_app(app)
migrate.init_app(app, db)

jobstores = { 
    'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
}

scheduler = BackgroundScheduler(jobstores=jobstores, timezone='EET')
if not scheduler.running:
    scheduler.start()


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# TODO: implement pagination

# it's important that the blueprints are imported after 
# the app and the db variable have been initialized
from project.auth.views import auth_blueprint
from project.cinema_reviews.views import cinema_review_blueprint
from project.cinemas.views import cinema_blueprint
from project.coupon_uses.views import coupon_use_blueprint
from project.coupons.views import coupon_blueprint
from project.faqs.views import faq_blueprint
from project.movie_reviews.views import movie_review_blueprint
from project.movies.views import movie_blueprint
from project.promo_codes.views import promo_code_blueprint
from project.scheduled_movies.views import scheduled_movie_blueprint 
from project.tickets.views import ticket_blueprint
from project.users.views import user_blueprint


app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(cinema_review_blueprint, url_prefix='/cinema_reviews')
app.register_blueprint(cinema_blueprint, url_prefix='/cinemas')
app.register_blueprint(coupon_use_blueprint, url_prefix='/coupon_uses')
app.register_blueprint(coupon_blueprint, url_prefix='/coupons')
app.register_blueprint(faq_blueprint, url_prefix='/faqs')
app.register_blueprint(movie_review_blueprint, url_prefix='/movie_reviews')
app.register_blueprint(movie_blueprint, url_prefix='/movies')
app.register_blueprint(promo_code_blueprint, url_prefix='/promo_codes')
app.register_blueprint(scheduled_movie_blueprint, url_prefix='/scheduled_movies')
app.register_blueprint(ticket_blueprint, url_prefix='/tickets')
app.register_blueprint(user_blueprint, url_prefix='/users')


from project.movies.movie_repository import MovieRepository
@app.route('/')
def index():
    # g = db.session.query(promo_code_uses).filter_by(user_id=1)
    # db.engine.execute(promo_code_uses.insert(), promo_code_id=1, user_id=1)
    # db.session.commit()
    # return "hello world!"
    # t1 = auth_utils.MANAGEMENT_API_TOKEN
    # auth_utils.update_management_api_token()
    # t2 = auth_utils.MANAGEMENT_API_TOKEN
    mv = MovieRepository()
    movies = mv.search('ultron')
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

    
# this endpoint if for testing purposes only. it is useful to avoid errors that arise 
# when the database in concurrently created from more than one gunicorn worker in build time 
# and it should be removed in production
@app.route('/init')
def init():
    db.engine.execute("DROP SCHEMA public CASCADE;")
    db.engine.execute("CREATE SCHEMA public;")

    db.create_all(app=app)
    
    import db_initialization_script
    
    return jsonify({
        'success': True
    }), 200
    
# from order id get the user id through a table and then verify the coupon payment
# and then update the coupon purchases table 
@app.route('/confirm_coupon_purchase', methods=['POST'])
def confirm_coupon_purchase():
    body = request.get_json()
    
    order_id = body['obj']['order']['id']
    transaction_id = body['obj']['id']
    
    coupon_purchase = Coupon_Purchase.query.filter_by(order_id=order_id).first()
    coupon_purchase.transaction_id = transaction_id
    coupon_purchase.is_paid = True
    coupon_purchase.purchase_date = datetime.now()
    
    coupon_purchase.update()
    
    expiry_time = datetime.now() + timedelta(days=7)
    scheduler.add_job(func=invalidate_coupon_purchase,
                      trigger='date', args=[coupon_purchase.id], 
                      run_date=expiry_time, 
                      misfire_grace_time=None,
                      id=f"invalidate coupon purchase {coupon_purchase.id} in {expiry_time}")
    
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