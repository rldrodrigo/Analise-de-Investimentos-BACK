from flask import Flask, session
from flask_restful import  Api
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
import pandas as pd
import json
import math
from datetime import datetime

from resources.tesouro import GetPrecoTaxa, GetTesouro, GetAnoVencimento, VendasTesouroDireto, PrecoTaxaTesouroDireto, OperacoesTesouroDireto
from resources.usuarios import SignIn, SignUp, SignOut, CheckIfLogged

app = Flask(__name__)
CORS(app)
api = Api(app)

# Utilizar o URI para quando estiver roando localmente e não pelo docker
# URI = "mongodb://localhost:27017/"
URI = "mongodb://db:27017"
client = MongoClient(URI)

# Definir a secret key do app
app.secret_key = b'\xe2\xaf\xbc:\xdd'

# rotas de dados brutos dos tesouros, serão utilizadas para popular o mongodb
api.add_resource(VendasTesouroDireto, '/api/vendasTesouroDireto/')
api.add_resource(PrecoTaxaTesouroDireto, '/api/precoTaxaTesouroDireto/')
#essa rota possui um alto volume de dados 1.6 Gb
api.add_resource(OperacoesTesouroDireto, '/api/operacoesTesouroDireto/')


# Rotas de dados filtrados
api.add_resource(GetTesouro, '/api/tesouro/getTesouro')
api.add_resource(GetPrecoTaxa, '/api/tesouro/getPrecoTaxa')
api.add_resource(GetAnoVencimento, '/api/tesouro/getAnoVencimento')

# Rotas de users
api.add_resource(SignIn, '/api/user/login')
api.add_resource(SignUp, '/api/user/signup')
api.add_resource(SignOut, '/api/user/signout')
api.add_resource(CheckIfLogged, '/api/user/checkLogged')

def PopularBanco():
    db = client["tfg-database"]
    db["vendaTesouros"].drop()
    
    VendasTesouroDiretoUrl = 'https://tesourotransparente.gov.br/ckan/dataset/f0468ecc-ae97-4287-89c2-6d8139fb4343/resource/e5f90e3a-8f8d-4895-9c56-4bb2f7877920/download/VendasTesouroDireto.csv'       
    df = pd.read_csv(VendasTesouroDiretoUrl, sep=';', decimal=',')
    data = df.to_json(orient="records")
    data = json.loads(data)
    Yi = 1
    for item in data:
        newDataVencimento = item['Vencimento do Titulo'].split('/')
        newDataVenda = item['Data Venda'].split('/')

        vencimento_titulo = datetime(int(newDataVencimento[2]), int(newDataVencimento[1]), int(newDataVencimento[0]))
        data_venda = datetime(int(newDataVenda[2]), int(newDataVenda[1]), int(newDataVenda[0]))

        newItem = {
            'tipo_titulo': item['Tipo Titulo'],
            'ano_vencimento': int(newDataVencimento[2]),
            'vencimento_titulo': vencimento_titulo,
            'data_venda': data_venda,
            'PU': item['PU'],
            'quantidade': item['Quantidade'],
            'valor': item['Valor'],
            # 'taxa_retorno': (item['PU'] - Yi)/Yi,
            # 'taxa_retorno': round((item['PU'] - Yi)/Yi*100, 2),
            # 'taxa_retorno_logaritmica':  math.log(item['PU']/Yi),
            # 'taxa_retorno_logaritmica':  round(math.log(item['PU']/Yi)*100, 2),
        }
        Yi = item['PU']
        db["vendaTesouros"].insert_one(newItem)

    db["precoTaxa"].drop()
    PrecoTaxaTesouroDiretoUrl = 'https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv'
    df2 = pd.read_csv(PrecoTaxaTesouroDiretoUrl, sep=';', decimal=',')
    tesouros = df2.to_json(orient="records")
    data = json.loads(tesouros)
    
    for item in data:
        newDataVencimento = item['Data Vencimento'].split('/')
        newDataBase = item['Data Base'].split('/')

        vencimento_titulo = datetime(int(newDataVencimento[2]), int(newDataVencimento[1]), int(newDataVencimento[0]))
        data_base = datetime(int(newDataBase[2]), int(newDataBase[1]), int(newDataBase[0]))

        newItem = {
            'tipo_titulo': item['Tipo Titulo'],
            'ano_vencimento': int(newDataVencimento[2]),
            'data_base': data_base,
            'taxa_compra_manha': item['Taxa Compra Manha'],
            'taxa_venda_manha': item['Taxa Venda Manha'],
            'pu_compra_manha': item['PU Compra Manha'],
            'pu_venda_manha': item['PU Venda Manha'],
            'pu_base_manha': item['PU Base Manha'],
            'vencimento_titulo': vencimento_titulo,
        }
        db["precoTaxa"].insert_one(newItem)
    return

if __name__ == '__main__':
    PopularBanco()
    app.run(debug=True, host='0.0.0.0', port=5000)