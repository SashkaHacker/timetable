from tables.user import Image
from tables import db_session
from os import path, mkdir
from secrets import token_hex
import os


def load_img(f, user, table, db_sess):
    exp = f.filename.split('.')[-1]
    filename = token_hex(16) + '.' + exp
    img = Image()
    img.owner_id = user
    img.parent_table = table
    img.hash = filename
    if not path.exists(path.join('static', 'images', str(user))):
        mkdir(path.join('static', 'images', str(user)))
    f.save(path.join('static', 'images', str(user), filename))
    db_sess.add(img)
    db_sess.commit()


def homework_edit(form, record, user):
    db_sess = db_session.create_session()
    if form.day.data:
        record.day = form.day.data
    if form.time.data:
        record.time = form.time.data
    if form.title.data:
        record.title = form.title.data
    if form.text.data:
        record.homework_text = form.text.data
    db_sess.commit()
    f = form.file.data
    if f.filename:
        for i in record.homework_img:
            os.remove(f"static/images/{record.owner_id}/{i.hash}")
            db_sess.delete(i)
        load_img(f, user.id, record.id, db_sess)
    db_sess.close()
