from flask import Flask
from eventerx.config import DevConfig


app = Flask(__name__)

app.config.from_object(DevConfig())


from eventerx.routes import *