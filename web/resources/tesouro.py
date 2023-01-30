from datetime import datetime
from flask import request
from click import argument
from flask_restful import Resource, reqparse
from flask_cors import cross_origin
import pandas as pd
import pymongo
from pymongo import MongoClient
import json
from bson import json_util
from datetime import datetime

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

class GetTesouro(Resource):
    @cross_origin()
    def get(self):
        tipo_titulo = request.args.get('tipo_titulo')
        ano_vencimento = request.args.get('ano_vencimento')
        data_inicial = request.args.get('data_inicial')
        data_final = request.args.get('data_final')

        nova_data_inicial = data_inicial.split('-')
        nova_data_final = data_final.split('-')

        nova_data_inicial = datetime(int(nova_data_inicial[2]), int(nova_data_inicial[1]), int(nova_data_inicial[0]))
        nova_data_final = datetime(int(nova_data_final[2]), int(nova_data_final[1]), int(nova_data_final[0]))

        # URI = "mongodb://localhost:27017/"
        URI = "mongodb://db:27017"
        client = MongoClient(URI)
        db = client["tfg-database"]
        collection = db["vendaTesouros"]
        if(ano_vencimento):
            dados = collection.find({
                "tipo_titulo" : tipo_titulo,
                "ano_vencimento": int(ano_vencimento),
                "data_venda": {
                    "$gte": nova_data_inicial,
                    "$lte": nova_data_final
                }
            }).sort( [("data_venda", pymongo.ASCENDING)] )
        else:
             dados = collection.find({
                "tipo_titulo": tipo_titulo,
                "data_venda": {
                    "$gte": nova_data_inicial,
                    "$lte": nova_data_final
                }
            }).sort( [("data_venda", pymongo.ASCENDING)] )
        result = []
        for data in dados:
            result.append(data)
        return json.loads(json_util.dumps(result))


class GetPrecoTaxa(Resource):
    @cross_origin()
    def get(self):
        tipo_titulo = request.args.get('tipo_titulo')
        ano_vencimento = request.args.get('ano_vencimento')
        data_inicial = request.args.get('data_inicial')
        data_final = request.args.get('data_final')

        nova_data_inicial = data_inicial.split('-')
        nova_data_final = data_final.split('-')

        nova_data_inicial = datetime(int(nova_data_inicial[2]), int(nova_data_inicial[1]), int(nova_data_inicial[0]))
        nova_data_final = datetime(int(nova_data_final[2]), int(nova_data_final[1]), int(nova_data_final[0]))

        # URI = "mongodb://localhost:27017/"
        URI = "mongodb://db:27017"
        client = MongoClient(URI)
        db = client["tfg-database"]
        collection = db["precoTaxa"]
        if(ano_vencimento):
            dados = collection.find({
                "tipo_titulo" : tipo_titulo,
                "ano_vencimento": int(ano_vencimento),
                "data_base": {
                    "$gte": nova_data_inicial,
                    "$lte": nova_data_final
                }
            }).sort( [("data_base", pymongo.DESCENDING)] )
        else:
            dados = collection.find({
                "tipo_titulo" : tipo_titulo,
                "data_base": {
                    "$gte": nova_data_inicial,
                    "$lte": nova_data_final
                }
            }).sort( [("data_base", pymongo.DESCENDING)] )
        result = []
        for data in dados:
            result.append(data)
        return json.loads(json_util.dumps(result))
