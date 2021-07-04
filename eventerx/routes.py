from datetime import datetime, timedelta
import re
from eventerx.utils import check_invitation_code
from secrets import token_hex

from flask import flash, render_template, request, abort
from flask.helpers import url_for
from flask_login import current_user, login_required, logout_user
from flask_login.utils import login_user
from flask_migrate import current
from werkzeug.utils import redirect

from eventerx import app, bcrypt, db
from eventerx.forms import CreateEventForm, LoginForm, RegisterSchoolForm, RegisterStaffForm
from eventerx.models import (EventProject, InvitationCode, SchoolInstitution,
                             StaffMember, Task, TaskState, Team, User)


@app.route("/")
@login_required
def homepage():
    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()
    if current_user.role.id != 3:  # only managers
        tasks = StaffMember.query.filter_by(
            user_id=current_user.id).first().tasks
        return render_template("eventerx/pages/admin_homepage.html", current_user=current_user, page={'title': 'dashboard'}, school=school)

    else:
        return render_template("eventerx/pages/homepage.html", current_user=current_user, page={'title': 'dashboard'}, school=school)


@app.route('/calendar')
@login_required
def calendar():
    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()
    return render_template('eventerx/pages/calendar.html', current_user=current_user, page={'title': 'calendar'}, school=school)


@app.route('/chat')
@login_required
def chat():
    return render_template("eventerx/pages/chat.html", current_user=current_user, page={'title': 'chat'})


@app.route('/events')
@login_required
def events():
    if current_user.role.id != 3:  # only managers
        return "<h1>Access denied</h1>", 403
    events = EventProject.query.filter_by().all()
    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()
    return render_template('eventerx/pages/events.html', current_user=current_user, page={'title': 'events'}, events=events, school=school)


@app.route('/add/event', methods=['GET', 'POST'])
@login_required
def add_event():
    if current_user.role.id != 3:  # only managers
        return "<h1>Access denied</h1>", 403

    form = CreateEventForm(request.form)
    if request.method == "POST" and form.validate():
        school_id = StaffMember.query.filter_by(user_id=current_user.id).first().school_institution_id
        event = EventProject(title=form.title.data, venue=form.venue.data, description=form.description.data,
                             start_date=form.start_date.data, due_date=form.due_date.data, budget=form.budget.data, school_institution_id=school_id)
        db.session.add(event)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        else:
            return redirect(url_for('events'))

    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()
    return render_template('eventerx/pages/add_event.html', current_user=current_user, page={'title': 'events'}, events=events, school=school, form=form)


# @app.route('/resources')
# @login_required
# def resources():
#     resources =
#     return render_template('eventerx/pages/resources.html', current_user=current_user, page={'title':'resources'})


@app.route('/settings')
@login_required
def settings():
    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()
    return render_template('eventerx/pages/settings.html', page={'title': 'settings'}, school=school)


@app.route('/tasks')
@login_required
def tasks():
    if current_user.role.id != 3:  # only managers
        return "<h1>Access denied</h1>", 403

    tasks = TaskState.query.filter(
        manager_matricule=current_user.manager.matricule)
    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()
    return render_template('eventerx/pages/tasks.html', current_user=current_user, page={'title': 'tasks'}, tasks=tasks, school=school)


@app.route('/staff')
@login_required
def staff():
    # refuse access to this page to non-school and manager users
    if current_user.role.id != 2 and current_user.role.id != 3:
        return "<h1>Access denied</h1>", 403

    if current_user.role.id == 2:  # if it is the school
        school_id = SchoolInstitution.query.filter_by(
            email=current_user.email).first().id

    else:  # if it the  manager
        school_id = StaffMember.query.filter_by(
            user_id=current_user.id).first().school_institution_id

    # getting the staff members for the current user's school
    staff = StaffMember.query.filter_by(school_institution_id=school_id).all()

    # get the invitation key to use for adding staff members
    invitation_code = InvitationCode.query.filter_by(purpose="staff").first()
    if invitation_code:
        invitation_code = invitation_code.code
        invitation_url = url_for(
            'invitation', purpose="staff", code=invitation_code, _external=True)
    else:
        invitation_url = None

    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()

    return render_template('eventerx/pages/staff.html', current_user=current_user, page={'title': 'staff'}, staff_members=staff, invitation_url=invitation_url, school=school)


@app.route('/invite/<string:purpose>/<string:code>')
def invitation(purpose, code):
    code = check_invitation_code(code)
    if code:

        if purpose.lower() == "staff":
            page_template = "add_staff"
            form = RegisterStaffForm()
            form.school_id = code.school_institution_id

        elif purpose.lower() == "student":
            page_template = "add_student.html"
            form = RegisterStaffForm()

        elif purpose.lower() == "attendee":
            page_template = "add_attendee.html"
            form = RegisterStaffForm()

        else:
            return abort(404)

    else:
        print("invalid code")
        return abort(404)

    return render_template(f"eventerx/pages/{page_template}.html", page={'title': page_template.replace('_', " ").title()}, form=form)


@app.route('/add/staff', methods=['GET', 'POST'])
def add_staff():
    form = RegisterStaffForm(request.form)
    form_view = request.referrer

    if request.method == "POST" and form.validate():
        password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        user = User(email=form.email.data, first_name=form.first_name.data,
                    last_name=form.last_name.data, password=password, role_id=6)
        db.session.add(user)
        try:
            db.session.flush()
            user_id = user.id
            staff = StaffMember(matricule=form.matricule.data, phone=form.phone_number.data,
                                user_id=user_id, school_institution_id=form.school_id.data)

            db.session.add(staff)
            db.session.commit()

        except:
            raise

        else:
            return redirect(url_for('login'))

    return redirect(form_view)


@app.route('/staff/<string:staff_id>')
@login_required
def staff_member_details(staff_id):
    if current_user.role.id != 3 and current_user.role.id != 2:
        return "<h1>Access denied</h1>", 403

    staff = StaffMember.query.get(staff_id)

    if not staff:
        return abort(404)

    staff_user = staff.user
    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()

    return render_template('eventerx/pages/staff_detail.html', page={'title': staff_user.fullname}, staff=staff, staff_user=staff_user, school=school)


@app.route('/make_manager/<string:staff_id>')
@login_required
def make_staff_manager(staff_id):
    # only school has the right to make staff member a manager
    if current_user.role.id != 2:
        return abort(404)

    staff = StaffMember.query.get(staff_id)

    # if the matricule passed matches no account
    if not staff:
        return abort(404)

    staff_user = User.query.get(staff.user_id)

    # if the staff member is already a mangger
    if staff_user.role.id == 3:
        return redirect(request.referrer)

    staff_user.role_id = 3
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise
    else:
        return redirect(request.referrer)


@app.route('/teams')
@login_required
def teams():
    if current_user.role.id != 3:
        return "<h1>Access denied</h1>", 403

    teams = Team.query.filter_by(manager_id=current.manager.id).all()
    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()
    return render_template('eventerx/pages/teams.html', current_user=current_user, page={'title': 'teams'}, teams=teams, school=school)


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

    return render_template("eventerx/pages/login.html", page={'title': "login"}, form=form)


@app.route("/register/school", methods=['GET', 'POST'])
def register_school():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))

    form = RegisterSchoolForm(request.form)
    if request.method == "POST" and form.validate():
        password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        school_user = User(email=form.email_address.data,
                           password=password, role_id=2)
        db.session.add(school_user)

        school = SchoolInstitution(email=form.email_address.data, name=form.name.data, address1=form.address1.data,
                                   address2=form.address2.data, phone=form.phone_number.data, pobox=form.pobox.data, website=form.website.data)
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

    return render_template("eventerx/pages/register_school.html", page={'title': "register school"}, form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/gen_link/<string:purpose>')
@login_required
def generate_link(purpose):
    if current_user.role.id != 3 and current_user.role.id != 2:  # only managers and school admins
        return "<h1>Access denied</h1>", 403

    # if it is a manager, get the school id via the StaffMember class
    if current_user.role.id == 3:
        school_id = StaffMember.query.filter_by(
            user_id=current_user.id).first().school_institution_id

    # if it is the school itself, get the id through the SchoolInstitution class using email
    else:
        school_id = SchoolInstitution.query.filter_by(
            email=current_user.email).first().id

    url_code = token_hex(8)
    duration = datetime.now() + timedelta(days=7)  # make validity only for 7 days
    db.session.add(InvitationCode(
        code=url_code, duration=int(duration.timestamp()), purpose=purpose, school_institution_id=school_id))

    try:
        db.session.commit()
    except:
        db.session.rollabck()
    else:
        return redirect(url_for('staff'))
