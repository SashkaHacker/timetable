from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email
from tables import db_session
from tables.user import User

required = 'Это обязательное поле'


def validate_email(form, field):
    db_sess = db_session.create_session()
    user = list(db_sess.query(User).filter(User.email == field.data))
    if user:
        raise ValidationError('Аккаунт с таким email уже существует')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', [DataRequired(required), validate_email])
    password = PasswordField('Пароль', [DataRequired(required)])
    password_repeat = PasswordField('Повторите пароль', [
                                        DataRequired(required),
                                        EqualTo('password', message="Пароли должны совпадать")]
                                    )
    name = StringField('Имя', [DataRequired(required)])
    surname = StringField("Фамилия", [DataRequired(required)])
    submit = SubmitField('Войти')