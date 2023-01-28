from flask import Flask, jsonify, request, session
from passlib.hash import pbkdf2_sha256
import uuid
from web.app import db

class User:

    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        return jsonify(user), 200
    
    def signup(self):

        # Criar o objeto do usuário
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "password": request.form.get('password')
        }

        # Encriptar a senha
        user['password'] = pbkdf2_sha256.encrypt(user['password'])

        # Verifica se o email já está cadastrado
        if db.users.find_one({ "email" : user['email' ]}):
            return jsonify({ "error": "Email já está sendo utilizado "}), 400

        if db.users.insert_one(user):
            return self.start_session(user)

        return user, 200
    
    def signout(self):
        session.clear()
        #return redirect('/')
        return jsonify({"message": "deslogado com sucesso"})

    def login(self):

        user = db.users.find_one({
            "email": request.form.get('email')
        })

        if user:
            return self.start_session(user)
        
        return jsonify({ "error" : "Credenciais inválidas"}), 401