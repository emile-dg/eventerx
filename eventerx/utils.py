import json
import os

from eventerx import PROJECT_FILES_FOLDER, db, bcrypt
from eventerx.models import Country, Town, UserRoles, User


def get_project_file(filename):
    try:
        with open( os.path.join(PROJECT_FILES_FOLDER, filename), "r") as raw_file:
            return raw_file.read()
    except:
        raise


def setup_cities():
    """Load the `cities.json` files and add the values to the db"""
    raw_file_content = get_project_file("cities.json")
    content = json.loads(raw_file_content)
    try:
        for country_item in content['countries']:
            country = Country(country_name=country_item.get('name'))
            db.session.add(country)
            db.session.flush()
            for town_item in country_item.get('towns'):
                town = Town(town_name=town_item.get('name'), country_id=country.id)
                db.session.add(town)
                db.session.flush()
        db.session.commit()

    except:
        db.session.rollback()
        raise

def setup_root_user():
    email = "emiledjida404@gmail.com"
    password = bcrypt.generate_password_hash("password").decode("utf-8")
    first_name = "Emile"
    last_name = "DJIDA G"
    role_id = 1

    try:
        db.session.add( User(email=email, password=password, first_name=first_name, last_name=last_name, role_id=role_id) )
        db.session.commit()
    except:
        db.session.rollback()
        raise


def setup_user_roles():
    raw_roles = json.loads(get_project_file("roles.json"))
    for role_item in raw_roles.get('roles'):
        user_role = UserRoles(id=role_item.get('id'), name=role_item.get('name'))
        db.session.add(user_role)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def setup_all():
    pass