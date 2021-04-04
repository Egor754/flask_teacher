import json
import os
from random import sample

from flask import Flask, render_template, abort
from flask_wtf import CSRFProtect, FlaskForm
from wtforms import StringField, RadioField, SubmitField, HiddenField
from wtforms.validators import InputRequired

app = Flask(__name__)

csrf = CSRFProtect(app)

SECRET_KEY = os.urandom(43)
app.config['SECRET_KEY'] = SECRET_KEY


class RequestForm(FlaskForm):
    name = StringField('Ваше имя', [InputRequired(message="Введите что-нибудь")])
    phone = StringField('Ваш телефон')
    goal = RadioField('goal', choices=[
        ("travel", "Для путешествий"),
        ("study", "Для школы"),
        ("work", "Для работы"),
        ("relocate", "Для переезда"),
    ])
    time = RadioField('time', choices=[
        ("1-2", "1-2 часа в неделю"),
        ("2-5", "2-5 часа в неделю"),
        ("5-7", "5-7 часа в неделю"),
        ("7-10", "7-10 часа в неделю"),
    ])
    submit = SubmitField('Найдите мне преподавателя')


class BookingForm(FlaskForm):
    name = StringField('Ваше имя', [InputRequired(message="Введите что-нибудь")])
    phone = StringField('Ваш телефон', [InputRequired(message="Введите что-нибудь")])
    client_weekday = HiddenField()
    client_time = HiddenField()
    client_teacher = HiddenField()
    submit = SubmitField('Записаться на пробный урок')


@app.route('/')
def index():
    with open("database/goals.json", "r", encoding='utf-8') as f:
        goals = json.load(f)
    with open("database/teachers.json", "r", encoding='utf-8') as f:
        teachers = json.load(f)
    random_teachers = sample(teachers, 6)
    return render_template('flask_teacher/index.html', goals=goals, teachers=random_teachers)


@app.route('/all/')
def all_teachers():
    with open("database/goals.json", "r", encoding='utf-8') as f:
        goals = json.load(f)
    with open("database/teachers.json", "r", encoding='utf-8') as f:
        teachers = json.load(f)
    return render_template('flask_teacher/all.html', goals=goals, teachers=teachers)


@app.route('/goals/<goal>/')
def goals(goal):
    with open("database/goals.json", "r", encoding='utf-8') as f:
        goals = json.load(f)
    if goal not in goals:
        abort(404)
    with open("database/teachers.json", "r", encoding='utf-8') as f:
        teachers = json.load(f)
    list_teachers = [teacher for teacher in teachers if goal in teacher['goals']]
    goal = goals[goal]
    return render_template('flask_teacher/goal.html', teachers=list_teachers, goal=goal)


@app.route('/profiles/<int:pk>/')
def profiles(pk):
    with open("database/week.json", "r", encoding='utf-8') as f:
        week = json.load(f)
    with open("database/teachers.json", "r", encoding='utf-8') as f:
        teacher = [item for item in json.load(f) if item.get('id') == pk]
    if not teacher:
        abort(404)
    with open("database/goals.json", "r", encoding='utf-8') as f:
        goals = json.load(f)
    return render_template('flask_teacher/profile.html', goals=goals, teacher=teacher[0], week=week)


@app.route('/request/', methods=['GET', 'POST'])
def order_request():
    form = RequestForm()
    if form.validate_on_submit():
        user = {'name': form.name.data, 'phone': form.phone.data, 'goal': form.goal.data, 'time': form.time.data}
        with open("database/request.json", "r", encoding='utf-8') as f:
            db = json.load(f)
        with open("database/request.json", "w", encoding='utf-8') as f:
            db['request_user'].append(user)
            json.dump(db, f, ensure_ascii=False, indent=4)
        with open("database/goals.json", "r", encoding='utf-8') as f:
            goal = json.load(f)
        user['goal'] = goal[user['goal']]
        return order_accepted(user)
    return render_template('flask_teacher/request.html', form=form)


@app.route('/request_done/')
def order_accepted(user):
    return render_template('flask_teacher/request_done.html', user=user)


@app.route('/booking/<int:pk>/<day>/<time>/', methods=['POST', 'GET'])
def booking(pk, day, time):
    time = time + ':00'
    form = BookingForm(client_weekday=day, client_time=time, client_teacher=pk)
    with open("database/teachers.json", "r", encoding='utf-8') as f:
        users = json.load(f)
    teacher = [user for user in users if user['id'] == pk]
    if not teacher:
        abort(404)
    with open("database/week.json", "r", encoding="utf-8") as f:
        week = json.load(f)
    name = teacher[0]['name']
    day_ru = week[day]
    if form.validate_on_submit():
        user = {'name': form.name.data, 'phone': form.phone.data, 'week_day': form.client_weekday.data,
                'time': form.client_time.data, 'id_teacher': form.client_teacher.data}
        with open("database/booking.json", "r", encoding='utf-8') as f:
            db = json.load(f)
            db['booking_user'].append(user)
        with open("database/booking.json", "w", encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
        user['week_day'] = day_ru
        return booking_accepted(user)
    return render_template('flask_teacher/booking.html', form=form, name=name, day_ru=day_ru, time=time)


@app.route('/booking_done/')
def booking_accepted(user):
    return render_template('flask_teacher/booking_done.html', user=user)


@app.errorhandler(404)
def page_not_found(error):
    return "<h1>Страничка не найдена</h1>", 404


@app.errorhandler(500)
def server_error(error):
    return "<h1>Всё очень плохо</h1>", 500


if __name__ == '__main__':
    app.run(debug=True)
