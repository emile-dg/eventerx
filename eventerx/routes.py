from flask import flash, render_template, request
from flask.helpers import url_for
from flask_login import current_user, login_required, logout_user
from flask_login.utils import login_user
from flask_migrate import current
from werkzeug.utils import redirect

from eventerx import app, bcrypt, db
from eventerx.forms import LoginForm, RegisterSchoolForm
from eventerx.models import Manager, SchoolInstitution, StaffMember, Task, TaskState, Team, User, EventProject


@app.route("/")
@login_required
def homepage():
    if current_user.role.id != 3: # only managers
        return render_template("eventerx/pages/admin_homepage.html", current_user=current_user, page={'title':'dashboard'})

    else:
        return render_template("eventerx/pages/homepage.html", current_user=current_user, page={'title':'dashboard'})


@app.route('/calendar')
@login_required
def calendar():
    return render_template('eventerx/pages/calendar.html', current_user=current_user, page={'title':'calendar'})


@app.route('/chat')
@login_required
def chat():
   return render_template("eventerx/pages/chat.html", current_user=current_user, page={'title':'chat'})


@app.route('/events')
@login_required
def events():
    if current_user.role.id != 3: # only managers
        return "<h1>Access denied</h1>", 403
    events = EventProject.query.filter_by().all()
    return render_template('eventerx/pages/events.html', current_user=current_user, page={'title':'events'}, events=events)


@app.route('/add/event', methods=['GET', 'POST'])
@login_required
def add_event():
    if current_user.role.id != 3: # only managers
        return "<h1>Access denied</h1>", 403
    return render_template('eventerx/pages/add_event.html', current_user=current_user, page={'title':''}, events=events)


@app.route('/profile')
@login_required
def profile():
    return render_template('eventerx/pages/profile.html', current_user=current_user, page={'title':'profile'})


# @app.route('/resources')
# @login_required
# def resources():
#     resources = 
#     return render_template('eventerx/pages/resources.html', current_user=current_user, page={'title':'resources'})


@app.route('/settings')
@login_required
def settings():
    return render_template('eventerx/pages/settings.html', current_user=current_user, page={'title':'settings'})


@app.route('/tasks')
@login_required
def tasks():
    if current_user.role.id != 3: # only managers
        return "<h1>Access denied</h1>", 403

    tasks = TaskState.query.filter(manager_matricule=current_user.manager.matricule)
    return render_template('eventerx/pages/tasks.html', current_user=current_user, page={'title':'tasks'}, tasks=tasks)


@app.route('/staff')
@login_required
def staff():
    if current_user.role.id != 2 or current_user.role.id != 3:
        return "<h1>Access denied</h1>", 403

    if current_user.role.id == 2:# if it the school
        school_id =  SchoolInstitution.query.filter_by(email=current_user.email)

    else: # if it the  manager
        school_id =  Manager.query.filter_by(user_id=current_user.id).first().school_institution_id

    staff = StaffMember.query.filter_by(school_institution_id = school_id).all()
    
    return render_template('eventerx/pages/staff.html', current_user=current_user, page={'title':'staff'}, staff=staff)


@app.route('/teams')
@login_required
def teams():
    if current_user.role.id != 3:
        return "<h1>Access denied</h1>", 403
    teams = Team.query.filter_by(manager_id=current.manager.id).all()
    return render_template('eventerx/pages/teams.html', current_user=current_user, page={'title':'teams'}, teams=teams)


@app.route("/login", methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('homepage'))

    form = LoginForm(request.form)
    if form.validate and request.method == "POST":
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            if not bcrypt.check_password_hash(user.password, form.password.data):
                flash("Invalid password", "error")
            else:
                login_user(user)
                return redirect(url_for('homepage'))
        else:
            flash("Invalid login credentials", "error")

    return render_template("eventerx/pages/login.html", form=form)


@app.route("/register/school", methods=['GET', 'POST'])
def register_school():
    form = RegisterSchoolForm(request.form)
    if request.method == "POST" and form.validate():
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        school_user = User(email=form.email_address.data, password=password, role_id=2)
        db.session.add(school_user)

        school = SchoolInstitution(email=form.email_address.data, name=form.name.data, address1=form.address1.data, address2=form.address2.data, phone=form.phone_number.data, pobox=form.pobox.data, website=form.website.data)
        db.session.add(school)

        try:
            db.session.commit()
        
        except:
            db.session.rollback()
            raise

        else:
            return redirect(url_for('login'))

    else:
        print(form.errors)

    return render_template("eventerx/pages/register_school.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))