from hashlib import sha256
from tables.user import User
from tables import db_session
from secrets import token_urlsafe


def reg(form):
    password = form.password.data
    form.password.data = sha256(form.password.data.encode('utf-8')).hexdigest()
    token = token_urlsafe(16)
    db_sess = db_session.create_session()
    user = User()
    user.name = form.name.data
    user.surname = form.surname.data
    user.email = form.email.data
    user.password = form.password.data
    user.token = token
    db_sess.add(user)
    db_sess.commit()
    db_sess.close()
    form.password.data = password
