import json
from random import sample

from flask import Flask, render_template, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect, FlaskForm
from wtforms import RadioField, StringField, SubmitField, HiddenField
from wtforms.validators import InputRequired

app = Flask(__name__)

csrf = CSRFProtect(app)

SECRET_KEY = 'secrvcvxvxcvxcvxcvdvfnghnhgczet_key'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teacher.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# class WeekDay(db.Model):
#     __tablename__ = 'weekday'
#     id = db.Column(db.Integer, primary_key=True)
#     day = db.Column(db.String(20))
#     day_ru = db.Column(db.String(100))
#
#
#
# class Time(db.Model):
#     __tablename__ = 'time'
#     id = db.Column(db.Integer, primary_key=True)
#     time = db.Column(db.String(15))
#     workload = db.Column(db.Boolean)
#
#
# day_time_teacher = db.Table(
#     "day_time_teacher",
#     db.Column("day_id", db.Integer, db.ForeignKey("weekday.id")),
#     db.Column("time_id", db.Integer, db.ForeignKey("time.id")),
#     db.Column("teacher_id", db.Integer, db.ForeignKey("teacher.id")),
# )
#
# teacher_goals = db.Table(
#     "teacher_goals",
#     db.Column("teacher_id", db.Integer, db.ForeignKey("teacher.id")),
#     db.Column("goal_id", db.Integer, db.ForeignKey("goals.id")),
# )
#
#
# class Teacher(db.Model):
#     __tablename__ = 'teacher'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(250))
#     about = db.Column(db.Text)
#     picture = db.Column(db.String(255))
#     rating = db.Column(db.Float)
#     price = db.Column(db.Integer)
#     goal = db.relationship(
#         "Goals", secondary=teacher_goals, back_populates="teacher"
#     )
#     student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
#     student = db.relationship('Student')
#     day = db.relationship(
#         "WeekDay", secondary=day_time_teacher, back_populates="weekday"
#     )
#     time = db.relationship(
#         "Time", secondary=day_time_teacher, back_populates="time"
#     )
#
#
# class Goals(db.Model):
#     __tablename__ = 'goals'
#     id = db.Column(db.Integer, primary_key=True)
#     goal = db.Column(db.String(255))
#     goal_ru = db.Column(db.String(255))
#     teacher = db.relationship(
#         "Teacher", secondary=teacher_goals, back_populates="goals"
#     )
#     selection = db.relationship("SelectionTeacher")
#
#
# class Student(db.Model):
#     __tablename__ = 'student'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255))
#     phone = db.Column(db.String(255))
#     teacher = db.relationship('Teacher')
#     selection = db.relationship('SelectionTeacher')
#
#
# class SelectionTeacher(db.Model):
#     __tablename__ = 'selection'
#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
#     student = db.relationship("Student")
#     goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'))
#     goal = db.relationship("Goals")
# db.create_all()
# with open('database/week.json',encoding='utf-8') as f:
#     a = json.load(f)
#
# for k,v in a.items():
#     day = WeekDay(k,v)
#     db.session.add(day)
# db.session.commit()

class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    about = db.Column(db.Text)
    rating = db.Column(db.Float)
    picture = db.Column(db.String(255))
    price = db.Column(db.Integer)
    goals = db.Column(db.String(255))
    free = db.Column(db.Text)
    booking = db.relationship('Booking', back_populates="teacher")


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    week_day = db.Column(db.String(40))
    time = db.Column(db.String(40))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    teacher = db.relationship('Teacher', back_populates="booking")


class Request(db.Model):
    __tablename__ = 'request'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    goal = db.Column(db.String(255))
    time = db.Column(db.String(10))


class RequestForm(FlaskForm):
    name = StringField('Ваше имя', [InputRequired(message="Введите что-нибудь")])
    phone = StringField('Ваш телефон', [InputRequired()])
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
