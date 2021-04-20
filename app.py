import json
from random import sample

import phonenumbers
from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect, FlaskForm
from wtforms import RadioField, StringField, SubmitField, SelectField
from wtforms.validators import InputRequired, ValidationError

app = Flask(__name__)

csrf = CSRFProtect(app)

SECRET_KEY = 'secrvcvxvxcvxcvxcvdvfnghnhgczet_key'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teacher.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

teacher_goals = db.Table(
    "teacher_goals",
    db.Column("teacher_id", db.Integer, db.ForeignKey("teacher.id")),
    db.Column("goal_id", db.Integer, db.ForeignKey("goals.id")),
)


class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String(255))
    goal_ru = db.Column(db.String(255))
    teacher = db.relationship('Teacher', secondary=teacher_goals, back_populates="goals")


class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    about = db.Column(db.Text)
    rating = db.Column(db.Float)
    picture = db.Column(db.String(255))
    price = db.Column(db.Integer)
    free = db.Column(db.Text)
    booking = db.relationship('Booking', back_populates="teacher")
    goals = db.relationship('Goal', secondary=teacher_goals, back_populates="teacher")


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

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Некорректный номер')


class BookingForm(FlaskForm):
    name = StringField('Ваше имя', [InputRequired(message="Введите что-нибудь")])
    phone = StringField('Ваш телефон', [InputRequired()])
    submit = SubmitField('Записаться на пробный урок')

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Некорректный номер')


class SortTeacherForm(FlaskForm):
    select_sort = SelectField('select_sort', choices=[
        ('random', 'В случайном порядке'),
        ('rating', 'Сначала лучшие по рейтингу'),
        ('max_price', 'Сначала дорогие'),
        ('min_price', 'Сначала недорогие'),
    ])


@app.route('/')
def index():
    goals = Goal.query.all()
    random_teachers = sample(Teacher.query.all(), 6)
    return render_template('flask_teacher/index.html', goals=goals, teachers=random_teachers)


@app.route('/all/', methods=['POST', 'GET'])
def all_teachers():
    form = SortTeacherForm()
    teacher_all = Teacher.query.all()
    teacher_count = Teacher.query.count()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.select_sort.data == 'rating':
                teacher_all = Teacher.query.order_by(Teacher.rating.desc())
            elif form.select_sort.data == 'random':
                teacher_all = sample(Teacher.query.all(), len(Teacher.query.all()))
            elif form.select_sort.data == 'max_price':
                teacher_all = Teacher.query.order_by(Teacher.price.desc())
            elif form.select_sort.data == 'min_price':
                teacher_all = Teacher.query.order_by(Teacher.price)
    return render_template('flask_teacher/all.html', teachers=teacher_all, form=form, teacher_count=teacher_count)


@app.route('/goals/<goal>/')
def goals(goal):
    teacher_goal = Goal.query.filter(Goal.goal == goal).first_or_404()
    return render_template('flask_teacher/goal.html', teachers=teacher_goal)


@app.route('/profiles/<int:pk>/')
def profiles(pk):
    teacher = Teacher.query.get_or_404(pk)
    with open("database/week.json", "r", encoding='utf-8') as f:
        week = json.load(f)
    free = json.loads(teacher.free)
    return render_template('flask_teacher/profile.html', teacher=teacher, week=week, free=free)


@app.route('/request/', methods=['GET', 'POST'])
def order_request():
    form = RequestForm()
    if form.validate_on_submit():  # message
        user = Request(
            name=form.name.data,
            phone=form.phone.data,
            time=form.time.data,
            goal=form.goal.data
        )
        db.session.add(user)
        db.session.commit()
        print(form.name.data, form.phone.data, form.goal.data, form.time.data)
        return order_accepted(user)
    return render_template('flask_teacher/request.html', form=form)


@app.route('/request_done/')
def order_accepted(user):
    return render_template('flask_teacher/request_done.html', user=user)


@app.route('/booking/<int:pk>/<day>/<time>/', methods=['POST', 'GET'])
def booking(pk, day, time):
    teacher = Teacher.query.get_or_404(pk)
    time = time + ':00'
    form = BookingForm()
    with open("database/week.json", "r", encoding="utf-8") as f:
        week = json.load(f)
    day_ru = week[day]
    if request.method == 'POST':
        if form.validate_on_submit():
            student = Booking(
                name=form.name.data,
                phone=form.phone.data,
                week_day=day_ru,
                time=time,
                teacher=teacher
            )
            db.session.add(student)
            db.session.commit()
            return booking_accepted(student)
    return render_template('flask_teacher/booking.html', form=form, name=teacher.name, day_ru=day_ru, time=time)


@app.route('/booking_done/')
def booking_accepted(stedunt):
    return render_template('flask_teacher/booking_done.html', user=stedunt)


@app.errorhandler(404)
def page_not_found(error):
    return "<h1>Страничка не найдена</h1>", 404


@app.errorhandler(500)
def server_error(error):
    return "<h1>Всё очень плохо</h1>", 500


if __name__ == '__main__':
    app.run(debug=True)
