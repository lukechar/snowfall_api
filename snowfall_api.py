from flask import Flask, request
from flask_restful import Api, Resource
from scraper import get_snow_report
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from functools import wraps

from resorts import resorts_list

import datetime
import json
import jwt
import atexit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisthesecretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')  # http://127.0.0.1:5000/route?token=[token here]
        if not token:
            return 'Missing token.', 403
        try:
            jwt.decode(token, app.config['SECRET_KEY'])
            return f(*args, **kwargs)
        except jwt.exceptions.InvalidTokenError:
            return 'Token is invalid', 403

    return decorated


def get_all_snow_reports():
    for resort, resort_url in resorts_list:
        result = get_snow_report(resort_url)
        # Save results to database
        sr = SnowReport(resort=resort, resort_url=resort_url, json_data=result)
        db.session.add(sr)
        db.session.commit()
        print("Saved snow report for {} to database".format(sr.resort))


class SnowReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    resort = db.Column(db.String(110), nullable=False)
    resort_url = db.Column(db.String(120), nullable=False)
    json_data = db.Column(db.JSON(1200), nullable=False)

    def __repr__(self):
        return self.resort


api = Api(app)


class GetSnowReport(Resource):
    @token_required
    def get(self, resort):
        sr_res = SnowReport.query.filter(SnowReport.resort_url == resort).order_by(SnowReport.time.desc()).first()
        if not sr_res:
            return 'No snow report for {} found.'.format(resort), 404
        serialized_report = sr_res.json_data
        serialized_report.update({'time': str(sr_res.time)})
        return serialized_report, 200


api.add_resource(GetSnowReport, "/snow_report/<string:resort>")

# Schedule snow report scraping
scheduler = BackgroundScheduler()
scheduler.add_job(func=get_all_snow_reports, trigger='interval', hours=1)
scheduler.start()
# Shutdown the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# GENERATE JWT TOKEN
# print('Token: {}'.format(jwt.encode({'user': 'luke'}, app.config['SECRET_KEY'], algorithm='HS256')))

# Run the server
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
