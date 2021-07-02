from wtforms import Form, StringField, PasswordField, validators


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
    password = PasswordField('Master Password')