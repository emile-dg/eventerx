from flask import render_template
from eventerx import app


@app.route("/")
def homepage():
    return render_template("eventerx/pages/homepage.html", page={'title':'dashboard'})


@app.route('/calendar')
def calendar():
    return render_template('eventerx/pages/calendar.html', page={'title':'calendar'})


@app.route('/chat')
def chat():
   return render_template("eventerx/pages/chat.html", page={'title':'chat'})


@app.route('/events')
def events():
    return render_template('eventerx/pages/events.html', page={'title':'events'})


@app.route('/profile')
def profile():
    return render_template('eventerx/pages/profile.html', page={'title':'profile'})


@app.route('/resources')
def resources():
    return render_template('eventerx/pages/resources.html', page={'title':'resources'})


@app.route('/settings')
def settings():
    return render_template('eventerx/pages/settings.html', page={'title':'settings'})


@app.route('/tasks')
def tasks():
    return render_template('eventerx/pages/tasks.html', page={'title':'tasks'})


@app.route('/teams')
def teams():
    return render_template('eventerx/pages/teams.html', page={'title':'teams'})


@app.route("/login")
def login():
    return render_template("eventerx/pages/login.html")


@app.route("/register/school")
def register_school():
    return render_template("eventerx/pages/register_school.html")
