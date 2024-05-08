from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField


class CheckoutForm(FlaskForm):
    id = StringField()
    submit = SubmitField("Выполнить")
    delete = SubmitField("Удалить")
