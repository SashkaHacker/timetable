from json import loads, dumps
from jsonschema import validate
from modules.schemas import LIST_SCHEMA, ADD_SCHEMA
from tables.user import User, Tables
from tables import db_session
from flask import Flask
from flask_restful import Resource, request
from datetime import datetime as dt


class TableListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        try:
            data = loads(request.get_data())
            validate(instance=data,
                     schema=LIST_SCHEMA)
            token = data.pop('token')
            user = db_sess.query(User).filter(User.token == token)[0]
            start = dt.strptime(data['start'], "%d-%m-%Y").date()
            end = dt.strptime(data['end'], "%d-%m-%Y").date()
            assert user

        except AssertionError:
            data = dumps({"error": "Неверный токен"})
            response = Flask.response_class(status=403,
                                            mimetype="application/json",
                                            response=data)
            return response

        except Exception as e:
            data = dumps({"error": str(e)})
            response = Flask.response_class(status=400,
                                            mimetype="application/json",
                                            response=data)
            return response
        response = list()
        for obj in db_sess.query(Tables).filter(Tables.day.between(start, end)):
            response.append(obj.to_dict())
        print(response)
        response = dumps(response)

        response = Flask.response_class(status=400,
                                        mimetype="application/json",
                                        response=response)
        return response


class TableResource(Resource):
    def post(self):
        db_sess = db_session.create_session()
        try:
            data = loads(request.get_data())
            validate(instance=data,
                     schema=ADD_SCHEMA)
            token = data.pop('token')
            user = db_sess.query(User).filter(User.token == token)[0]
            data['time'] = dt.strptime(data['time'], "%H:%M").time()
            data['day'] = dt.strptime(data['day'], "%m-%d-%Y").date()
            assert user

        except AssertionError:
            data = dumps({"error": "Неверный токен"})
            response = Flask.response_class(status=403,
                                            mimetype="application/json",
                                            response=data)
            return response

        except Exception as e:
            data = dumps({"error": str(e)})
            response = Flask.response_class(status=400,
                                            mimetype="application/json",
                                            response=data)
            return response

        data['owner_id'] = user.id
        table = Tables(**data)
        db_sess.add(table)
        db_sess.commit()
        db_sess.close()
        response = Flask.response_class(status=200)
        return response
