import os

from flask import Flask, render_template, url_for, request, redirect, abort, jsonify, send_file
from flask_login import LoginManager, login_required, logout_user, current_user
from flask_restful import Api
from forms.login import LoginForm
from forms.homework import HomeworkForm
from forms.register import RegisterForm
from modules.homework import homework_form
from forms.checkout import CheckoutForm
from modules.registration import reg
from modules.edit_homework import homework_edit
from modules.api import TableResource, TableListResource
from modules.login import login
from tables.user import User, Tables, Image
from tables import db_session
from secrets import token_urlsafe
# from threading import Thread
# import bot

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456789qwerty'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)
api.add_resource(TableResource, "/add_work")
api.add_resource(TableListResource, "/homework_list")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if user.is_ban:
        return
    return user


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect("/user")
    return render_template('welcome.html')


@app.route('/admin')
def admin():
    if current_user.is_authenticated:
        if current_user.is_admin:
            db_sess = db_session.create_session()
            n = int(request.args.get('page', 1))
            admin = int(request.args.get('admin', 0))
            ban = int(request.args.get('ban', 0))
            if admin:
                new_admin = db_sess.query(User).get(admin)
                new_admin.is_admin = not new_admin.is_admin
                db_sess.commit()
            elif ban:
                banned = db_sess.query(User).get(ban)
                banned.is_ban = not banned.is_ban
                db_sess.commit()
            users = list(db_sess.query(User))
            return render_template("admin.html", admin=current_user, users=users, n=n)
    return render_template('welcome.html')


@app.route("/user")
def user():
    if current_user.is_authenticated:
        new_token = int(request.args.get('token', 0))
        if new_token:
            db_sess = db_session.create_session()
            current_user.connection = None
            current_user.token = token_urlsafe(16)
            db_sess.commit()
            return redirect("/user")
        else:
            return render_template(
                "user_cabinet.html",
                title="Личный кабинет",
                user=current_user)
    else:
        return redirect("/")


@app.route('/calendar', methods=["POST", "GET"])
def timetable():
    if request.method == "GET":
        return render_template('calendar.html')
    if request.method == "POST":
        return redirect('/login')


@app.route('/jsoncalendar')
def json_timetable():
    if current_user.is_authenticated:
        start = request.args.get('start')
        end = request.args.get('end')
        result = []
        db_sess = db_session.create_session()
        for obj in db_sess.query(Tables).filter(Tables.day.between(start, end), Tables.owner_id == current_user.id):
            print(type(obj.day))
            a = {
                'title': f' - {obj.title}',
                'start': f"{obj.day}T{obj.time}",
                'end': f"{obj.day}T{obj.time}",
                'url': url_for('school_schedule_num', number=obj.id)
            }
            if obj.completed:
                a['color'] = 'green'
            else:
                a['color'] = 'red'
            result.append(a)

        return jsonify(result)
    else:
        return redirect("/welcome")


@app.route('/picture/<hash>')
@login_required
def picture(hash):
        pics = current_user.images
        pic = pics.filter(Image.hash == hash)[0]
        if pic:
            user_id = str(current_user.id)
            return send_file('static/images/' + user_id + '/' + pic.hash,
                             mimetype='image')
        else:
            abort(404)


@app.route("/homework", methods=["POST", "GET"])
def homework():
    form = HomeworkForm()
    if request.method == "GET":
        return render_template('add_homework.html', title="Запись", form=form)
    if request.method == "POST":
        homework_form(form, current_user)
        return redirect('/homework')


@app.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit(id):
    db_sess = db_session.create_session()
    form = HomeworkForm()
    table = db_sess.query(Tables).get(id)
    if table and table.owner_id == current_user.id:
        if request.method == "GET":
            record = table
            return render_template("edit_homework.html", title="Редактирование", form=form,
                                   table=record)
        if request.method == "POST":
            record = db_sess.query(Tables).get(id)
            homework_edit(form, record, current_user)
            return redirect(f"/school_schedule/{id}")
    abort(403)


@app.route("/school_schedule", methods=["GET", "POST"])
@login_required
def school_schedule():
    form = CheckoutForm()
    n = int(request.args.get('num', 1))
    if request.method == "GET":
        return render_template(
            "school_schedule.html",
            title="Расписание",
            form=form,
            n=n,
            user=current_user,
            table=list(current_user.table.filter(Tables.completed == False))
        )
    if request.method == "POST":
        db_sess = db_session.create_session()
        record = current_user.table.filter(Tables.id == form.id.data)[0]
        record.completed = True
        db_sess.commit()
        return render_template(
            "school_schedule.html",
            title="Расписание",
            user=current_user,
            n=n,
            form=form,
            table=list(current_user.table.filter(
                Tables.completed == False,
                Tables.active == True)
            )
            )


@app.route("/archive", methods=["GET", "POST"])
@login_required
def archive():
    form = CheckoutForm()
    n = int(request.args.get('num', 1))
    if request.method == "GET":
        return render_template(
            "archive.html",
            title="Расписание",
            form=form,
            n=n,
            user=current_user,
            table=list(current_user.table.filter(Tables.completed == True))
        )


@app.route("/school_schedule/<int:number>", methods=["GET", "POST"])
@login_required
def school_schedule_num(number):
    form = CheckoutForm()
    db_sess = db_session.create_session()
    if request.method == "GET":
        table = db_sess.query(Tables).get(number)
        if not table:
            abort(404)
        elif table.owner_id == current_user.id:
            return render_template(
                "homework.html",
                title=table.title,
                user=current_user,
                table=table,
                form=form)
        else:
            abort(403)
    if request.method == "POST":
        if form.id.data == "delete":
            table = db_sess.query(Tables).get(number)
            db_sess.delete(table)
            db_sess.commit()
            return render_template("delete.html", title="Запись удалена")
        if form.id.data == "hide":
            table = db_sess.query(Tables).get(number)
            table.completed = True
            db_sess.commit()
            return render_template("text_archive.html", title="Добавлено в архив")


@app.route('/registration', methods=["POST", "GET"])
def registration():
    if current_user.is_authenticated:
        return redirect("/user")
    form = RegisterForm()
    print('Я тут!')
    # if form.validate_on_submit():
    if form.is_submitted():
        print('Меня тут нет')
        db_sess = db_session.create_session()
        count = len(list(db_sess.query(User).filter(User.email == form.email.data)))
        db_sess.close()
        reg(form)
        login(form.email.data, form.password.data)
        return redirect('/')
    return render_template('registration.html', form=form)


@app.route("/login", methods=["POST", "GET"])
def authorization():
    if current_user.is_authenticated:
        return redirect("/user")
    form = LoginForm()
    if request.method == "GET":
        return render_template('authorization.html', form=form)
    if request.method == "POST":
        if login(form.email.data, form.password.data) is True:
            return redirect("/")
        if login(form.email.data, form.password.data) == "BAN":
            return render_template('authorization.html', form=form, flag_ban=True)
        return render_template('authorization.html', form=form, flag=True)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    db_session.global_init('db/db.db')
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run(host='127.0.0.1', port=8080, debug=True)
