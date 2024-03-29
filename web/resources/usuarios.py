from flask import Flask, jsonify, request, session
from flask_cors import CORS, cross_origin
from flask_restful import Resource
import uuid
from passlib.hash import pbkdf2_sha256
from pymongo import MongoClient

# Configuração da conexão com o banco
# URI = "mongodb://localhost:27017/"
URI = "mongodb://db:27017"
client = MongoClient(URI)
db = client["tfg-database"]
users = db["users"]

def start_session(user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        return jsonify(user), 200
class SignUp(Resource):

    @cross_origin()
    def post(self):

        postedData = request.get_json()

        user = {
            "_id": uuid.uuid4().hex,
            "name": postedData['name'],
            "email": postedData['email'],
            "password": postedData['password']
        }

        # Encriptar a senha
        user['password'] = pbkdf2_sha256.encrypt(user['password'])

        # Verifica se o email já está cadastrado
        if users.find_one({ "email" : user['email']}):
            return jsonify({ "error": "Email já está sendo utilizado "}), 301

        if users.insert_one(user):
            return start_session(user)

        return jsonify({ "error": "Não foi possível cadastrar "}), 400

class SignIn(Resource):

    @cross_origin()
    def post(self):
        postedData = request.get_json()

        user = users.find_one({
            "email": postedData['email']
        })

        if user and pbkdf2_sha256.verify(postedData['password'], user['password']):
            return start_session(user)

        return jsonify({
            "status": 301,
            "error" : "Credenciais inválidas" 
        }), 301

        

class SignOut(Resource):
    @cross_origin()
    def get(self):
        session.clear()

        return jsonify({
            "status": 200,
            "message": "Usuário deslogado com suceso"
        }), 200

class CheckIfLogged(Resource):
    @cross_origin()
    def get(self):
        if( 'logged_in' in session):
            return  jsonify(session), 200
            
        else:
            return jsonify({
                "status": 302,
                "logged_in": False,
                "message": "Usuário não autenticado",
            }), 302