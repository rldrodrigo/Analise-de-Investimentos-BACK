from pymongo import MongoClient
import pandas as pd
import pymongo

import datetime

URI = 'mongodb://localhost:27017'
client = MongoClient(URI)

db = client['tfg-database']

collection = db.tesouros
#collection = db['tesouros']


# tesouro = {"author": "Mike",
#         "text": "My first blog post!",
#         "tags": ["mongodb", "python", "pymongo"],
#         "date": datetime.datetime.utcnow()}

#db.tesouros

# para inserir um valor na collection tesouros
# posts = db.tesouros
# post_id = posts.insert_one(tesouro).inserted_id

## para listar todas as colllectiosn
# db.list_collection_names()

# posts.find_one()
URI = "mongodb://localhost:27017/"
client = MongoClient(URI)
db = client["tfg-database"]
collection = db["tesouros"]


dados = collection.find({"Tipo Titulo":"Tesouro Selic"})

for data in dados:
    print(data)

print(db.list_collection_names())

client.close()