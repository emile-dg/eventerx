from wtforms import (DateField, Form, HiddenField, IntegerField, PasswordField,
                     StringField, validators, TextAreaField)


class LoginForm(Form):
    email = StringField('Email', [validators.Email()])
    password = PasswordField('Password')


class RegisterSchoolForm(Form):
    name = StringField('Institution / School name', validators=[validators.DataRequired()])
    phone_number = StringField('Phone Number', validators=[validators.DataRequired()])
    address1 = StringField('Address 1', validators=[validators.DataRequired()])
    address2 = StringField('Address 2')
    pobox = StringField('PO BOX')
    email_address = StringField('Email', validators=[validators.DataRequired()])
    website = StringField('School Website')
    password = PasswordField('Master Password', validators=[validators.DataRequired()])


class RegisterStaffForm(Form):
    first_name = StringField('First Name', validators=[validators.DataRequired()])
    last_name = StringField('Last Name', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.DataRequired()])
    matricule = StringField('Matricule', validators=[validators.DataRequired()])
    phone_number = StringField('Phone Number', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    school_id = HiddenField(validators=[validators.DataRequired()])


class CreateEventForm(Form):
    title = StringField('Title', validators=[validators.DataRequired()])
    venue = StringField('Venue', validators=[validators.DataRequired()])
    description = TextAreaField("Description (Optional)", validators=[validators.Length(max=512)])
    budget = IntegerField('Budget', validators=[validators.DataRequired()])
    start_date = DateField('Event start date', validators=[validators.DataRequired()])
    due_date = DateField('Event End date', validators=[validators.DataRequired()])
