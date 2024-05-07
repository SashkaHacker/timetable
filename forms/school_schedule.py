from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ScheduleForm(FlaskForm):
    day = StringField(validators=[DataRequired()])
    lesson1 = StringField(validators=[DataRequired()])
    lesson2 = StringField(validators=[DataRequired()])
    lesson3 = StringField(validators=[DataRequired()])
    lesson4 = StringField(validators=[DataRequired()])
    lesson5 = StringField(validators=[DataRequired()])
    lesson6 = StringField(validators=[DataRequired()])
    lesson7 = StringField(validators=[DataRequired()])
    lesson8 = StringField(validators=[DataRequired()])
    submit = SubmitField('Сохранить')
