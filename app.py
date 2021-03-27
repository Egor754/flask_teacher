import json
from random import sample

from flask import Flask, render_template, abort

app = Flask(__name__)


# @app.context_processor
# def title_departures():
#     with open("goals.json", "r", encoding='utf-8') as f:
#         goals = json.load(f)
#     return goals


@app.route('/')
def index():
    with open("goals.json", "r", encoding='utf-8') as f:
        goals = json.load(f)
    with open("teachers.json", "r", encoding='utf-8') as f:
        teachers = json.load(f)
    random_teachers = sample(teachers, 6)
    return render_template('flask_teacher/index.html', goals=goals, teachers=random_teachers)


@app.route('/all/')
def all_teachers():
    with open("goals.json", "r", encoding='utf-8') as f:
        goals = json.load(f)
    with open("teachers.json", "r", encoding='utf-8') as f:
        teachers = json.load(f)
    return render_template('flask_teacher/all.html', goals=goals, teachers=teachers)


@app.route('/goals/<goal>/')
def goals(goal):
    return render_template('flask_teacher/goal.html')


@app.route('/profiles/<int:pk>/')
def profiles(pk):
    with open("week.json", "r", encoding='utf-8') as f:
        week = json.load(f)
    with open("teachers.json", "r", encoding='utf-8') as f:
        teacher = [item for item in json.load(f) if item.get('id') == pk]
    if not teacher:
        abort(404)
    with open("goals.json", "r", encoding='utf-8') as f:
        goals = json.load(f)
    print(teacher)
    return render_template('flask_teacher/profile.html', goals=goals, teacher=teacher[0],week=week)


@app.route('/request/', methods=['POST'])
def order_request():
    return render_template('flask_teacher/request.html')


@app.route('/request_done/')
def order_accepted():
    return render_template('flask_teacher/request_done.html')


@app.route('/booking/<int:pk>/<day>/<time>/')
def booking(pk, day, time):
    return render_template('flask_teacher/booking.html')


@app.route('/booking_done/')
def booking_accepted():
    return render_template('flask_teacher/booking_done.html')


if __name__ == '__main__':
    app.run(debug=True)
