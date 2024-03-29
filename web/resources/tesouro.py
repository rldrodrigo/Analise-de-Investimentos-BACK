from datetime import datetime
from flask import request
from click import argument
from flask_restful import Resource, reqparse
from flask_cors import cross_origin
import pandas as pd
import pymongo
import math
from pymongo import MongoClient
import json
from bson import json_util
from datetime import datetime
import random
import numpy as np

# URI = "mongodb://localhost:27017/"
URI = "mongodb://db:27017"
client = MongoClient(URI)
db = client["tfg-database"]

def calcular_volatilidade(S, media_S):
    diferenca_media = S - media_S
    diferenca_quadrada = diferenca_media**2
    volatilidade = np.sqrt(np.sum(diferenca_quadrada))
    return volatilidade

class GetTesouro(Resource):
    @cross_origin()
    def post(self):
        postedData = request.get_json()
        tipo_titulo = postedData['tipo_titulo']
        ano_vencimento = postedData['ano_vencimento']
        data_inicial = postedData['data_inicial']
        data_final = postedData['data_final']

        nova_data_inicial = data_inicial.split('-')
        nova_data_final = data_final.split('-')

        nova_data_inicial = datetime(int(nova_data_inicial[2]), int(nova_data_inicial[1]), int(nova_data_inicial[0]))
        nova_data_final = datetime(int(nova_data_final[2]), int(nova_data_final[1]), int(nova_data_final[0]))
        collection = db["vendaTesouros"]
        
        dados = collection.find({
            "tipo_titulo" : tipo_titulo,
            "ano_vencimento": int(ano_vencimento),
            "data_venda": {
                "$gte": nova_data_inicial,
                "$lte": nova_data_final
            }
        }).sort( [("data_venda", pymongo.ASCENDING)])

        result = []
        for data in dados:
            newItem = {
                'tipo_titulo': data['tipo_titulo'],
                'ano_vencimento': data['ano_vencimento'],
                'vencimento_titulo': data['vencimento_titulo'],
                'data_venda': data['data_venda'],
                'PU': data['PU'],
                'quantidade': data['quantidade'],
                'valor': data['valor'],
            }
            result.append(newItem)
        return json.loads(json_util.dumps(result))

class GetPrecoTaxa(Resource):
    @cross_origin()
    def post(self):
        postedData = request.get_json()
        tipo_titulo = postedData['tipo_titulo']
        ano_vencimento = postedData['ano_vencimento']
        data_inicial = postedData['data_inicial']
        data_final = postedData['data_final']

        Yi = 1
        listaRetornos = []
        pk = 1
        nc = 1.65
        # nc é o nível de confiança NC(95%) = 1,65; NC (97,5%) = 1,96; NC (90%) = 1,28).

        nova_data_inicial = data_inicial.split('-')
        nova_data_final = data_final.split('-')

        nova_data_inicial = datetime(int(nova_data_inicial[2]), int(nova_data_inicial[1]), int(nova_data_inicial[0]))
        nova_data_final = datetime(int(nova_data_final[2]), int(nova_data_final[1]), int(nova_data_final[0]))
        collection = db["precoTaxa"]
        if(ano_vencimento):
            dados = collection.find({
                "tipo_titulo" : tipo_titulo,
                "ano_vencimento": int(ano_vencimento),
                "data_base": {
                    "$gte": nova_data_inicial,
                    "$lte": nova_data_final
                }
            }).sort( [("data_base", pymongo.ASCENDING)] )
        else:
            dados = collection.find({
                "tipo_titulo" : tipo_titulo,
                "data_base": {
                    "$gte": nova_data_inicial,
                    "$lte": nova_data_final
                }
            }).sort( [("data_base", pymongo.ASCENDING)] )
        result = []
        for data in dados:
            retorno = 0 if Yi == 1 else ( data['pu_base_manha'] - Yi)/Yi
            listaRetornos.append(retorno)
            Si = np.array(listaRetornos)
            media_S = np.mean(Si)
            volatilidade = np.sqrt((retorno - media_S)**2)
            newItem = {
                'tipo_titulo': data['tipo_titulo'],
                'ano_vencimento': data['ano_vencimento'],
                'vencimento_titulo': data['vencimento_titulo'],
                'data_base': data['data_base'],
                'pu_base_manha': data['pu_base_manha'],
                'pu_compra_manha': data['pu_compra_manha'],
                'pu_venda_manha': data['pu_venda_manha'],
                'taxa_compra_manha': data['taxa_compra_manha'],
                'taxa_venda_manha': data['taxa_venda_manha'],
                'taxa_retorno': retorno,
                # 'taxa_retorno': round((item['PU'] - Yi)/Yi*100, 2),
                'taxa_retorno_logaritmica':  math.log(data['pu_base_manha']/Yi),
                'risco': volatilidade,
                'value_at_risk': 0 if Yi == 1 else -1000*nc*volatilidade
                # Utilizando investimento de 1000 como base, depois alterar para ser possível o usuário digitar
                # 'taxa_retorno_logaritmica':  round(math.log(item['PU']/Yi)*100, 2),
            }
            Yi = data['pu_base_manha']
            result.append(newItem)
        
        return json.loads(json_util.dumps(result))

class GetAnoVencimento(Resource):
    @cross_origin()
    def post(self):

        postedData = request.get_json()
        tipo_titulo =  postedData['tipo_titulo']
        collection = db["vendaTesouros"]

        dados = collection.find({ "tipo_titulo": tipo_titulo }).distinct("ano_vencimento")
        result = []
        for data in dados:
            result.append(data)
        return json.loads(json_util.dumps(result))
    
class GetTaxaRetorno(Resource):
    @cross_origin()
    def post(self):

        postedData = request.get_json()
        tipo_titulo =  postedData['tipo_titulo']
        periodo = postedData['periodo']
        collection = db["vendaTesouros"]

        dados = collection.find({ "tipo_titulo": tipo_titulo }).distinct("ano_vencimento")
        result = []
        for data in dados:
            result.append(data)
        return json.loads(json_util.dumps(result))

# Rotas de dados brutos
class VendasTesouroDireto(Resource):
    @cross_origin()
    def get(self):
        VendasTesouroDiretoUrl = 'https://tesourotransparente.gov.br/ckan/dataset/f0468ecc-ae97-4287-89c2-6d8139fb4343/resource/e5f90e3a-8f8d-4895-9c56-4bb2f7877920/download/VendasTesouroDireto.csv'       
        df = pd.read_csv(VendasTesouroDiretoUrl, sep=';', decimal=',')
        return df.to_json(orient="records")

class PrecoTaxaTesouroDireto(Resource):
    @cross_origin()
    def get(self):
        PrecoTaxaTesouroDiretoUrl = 'https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv'
        df = pd.read_csv(PrecoTaxaTesouroDiretoUrl, sep=';', decimal=',')
        tesouros = df.to_json(orient="records")
        return tesouros

class OperacoesTesouroDireto(Resource):
    @cross_origin()
    def get(self):
        # Operação muito longa por que a planilha tem 1.6Gb
        OperacoesTesouroDiretoUrl = 'https://www.tesourotransparente.gov.br/ckan/dataset/78739a33-4d2f-4e35-88fd-65f1ccbe81c4/resource/4100d614-d1ad-4b62-9435-84f7943e46f3/download/OperacoesTesouroDireto.csv'
        df = pd.read_csv(OperacoesTesouroDiretoUrl, sep=';', decimal=',')
        return df.to_json(orient="records")
