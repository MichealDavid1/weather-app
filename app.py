import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages
)
from flask_sqlalchemy import SQLAlchemy
import sys
import requests

app = Flask(__name__)

db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SECRET_KEY'] = os.urandom(29)


class City(db.Model):
    __tablename__ = 'city'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)


db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    url = 'https://api.openweathermap.org/data/2.5/weather'
    if request.method == 'POST':
        city = City.query.filter_by(name=request.form['city_name']).first()
        if city is not None:
            flash("The city has already been added to the list!")
            return redirect(url_for('index'))
        else:
            params = {
                'q': request.form['city_name'],
                'appid': 'e9f38a1b4fb975b320903c10fa4c2011'
            }
            r = requests.get(url, params=params)
            try:
                if r.json()['message'] == 'city not found':
                    flash("The city doesn't exist!")
                    return redirect(url_for('index'))
            except KeyError:
                city = City(name=request.form['city_name'])
                db.session.add(city)
                db.session.commit()

    cities = City.query.all()
    weather = []
    for city in cities:
        params = {
            'q': city.name,
            'appid': 'e9f38a1b4fb975b320903c10fa4c2011'
        }
        r = requests.get(url, params=params)
        data = {
            'state': r.json()['weather'][0]['main'],
            'temp': r.json()['main']['temp'],
            'city': city.name.upper(),
            'id': city.id
        }
        weather.append(data)
    if len(weather) == 0:
        weather = False
    return render_template('index.html', data=weather)


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    if city is None:
        flash("The city doesn't exist!")
        return redirect('/')
    else:
        db.session.delete(city)
        db.session.commit()
        return redirect('/')


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
