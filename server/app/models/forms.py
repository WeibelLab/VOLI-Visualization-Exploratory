from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, BooleanField, HiddenField

from wtforms import validators, ValidationError
from wtforms.validators import DataRequired

class Response(FlaskForm):
    requestId = HiddenField()
    deviceId = HiddenField()
    sessionId = HiddenField()
    query = HiddenField()
    response = HiddenField()
    cardtitle = TextField()