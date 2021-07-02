class DevConfig:
    SECRET_KEY = 'thisisakey'
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "mysql://emiledjida:emiledjida@localhost:3306/eventerx"