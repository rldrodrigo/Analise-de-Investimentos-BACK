from flask import Flask, jsonify, request, session
from flask_cors import cross_origin
from flask_restful import Resource
import uuid
from passlib.hash import pbkdf2_sha256
from pymongo import MongoClient

def start_session(user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        print(session)
        return jsonify(user), 200

class SignUp(Resource):

    @cross_origin()
    def post(self):

        data = request.get_json()

        user = {
            "_id": uuid.uuid4().hex,
            "name": data['name'],
            "email": data['email'],
            "password": data['password']
        }

        # Encriptar a senha
        user['password'] = pbkdf2_sha256.encrypt(user['password'])

        # Configuração da conexão com o banco
        URI = "mongodb://localhost:27017/"
        client = MongoClient(URI)
        db = client["tfg-database"]
        collection = db["users"]

        # Verifica se o email já está cadastrado
        if collection.find_one({ "email" : user['email']}):
            return jsonify({ "error": "Email já está sendo utilizado "}), 400

        if collection.insert_one(user):
            return start_session(user)

        return jsonify({ "error": "Não foi possível cadastrar "}), 400

class SignIn(Resource):

    @cross_origin()
    def post(self):
        data = request.get_json()

        # Configuração da conexão com o banco
        URI = "mongodb://localhost:27017/"
        client = MongoClient(URI)
        db = client["tfg-database"]
        collection = db["users"]

        user = collection.find_one({
            "email": data['email']
        })

        if user and pbkdf2_sha256.verify(data['password'], user['password']):
            return start_session(user)
        
        return jsonify({ "error" : "Credenciais inválidas" })

        

class SignOut(Resource):
    @cross_origin()
    def get(self):
        session.clear()
        return jsonify({"message": "Usuário deslogado com suceso"})

class CheckIfLogged(Resource):
    @cross_origin()
    def get(self):
        if( 'logged_in' in session):
            return  jsonify(session)
        else:
            return jsonify(session)