from datetime import datetime
from flask import request
from click import argument
from flask_restful import Resource, reqparse
from flask_cors import cross_origin
import pandas as pd
from pymongo import MongoClient
import json
from bson import json_util

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
        # argumentos = reqparse.RequestParser()
        # argumentos.add_argument('tesouro_type', required=True, help='Treasury type cannot be blank')
        # args = argumentos.parse_args()
        tesouro_type = request.args.get('tesouro_type')
        
        if tesouro_type == "1":
            argumento = "Tesouro IGPM+ com Juros Semestrais"
        elif tesouro_type == "2":
            argumento = "Tesouro Selic"
        elif tesouro_type == "3":
            argumento = "Tesouro IPCA+"
        elif tesouro_type == "4":
            argumento = "Tesouro IPCA+ com Juros Semestrais"
        elif tesouro_type == "5":
            argumento = "Tesouro Prefixado com Juros Semestrais"
        elif tesouro_type == "6":
            argumento = "Tesouro Prefixado"
        else: 
            argumento = "Tesouro Selic"
        print(tesouro_type, argumento)

        URI = "mongodb://localhost:27017/"
        client = MongoClient(URI)
        db = client["tfg-database"]
        collection = db["tesouros"]
        dados = collection.find({"Tipo Titulo" : argumento })
        result = []
        for data in dados:
            result.append(data)
        return json.loads(json_util.dumps(result))


class GetPrecoTaxa(Resource):
    @cross_origin()
    def get(self):
        tesouro_type = request.args.get('tesouro_type')
        
        if tesouro_type == "1":
            argumento = "Tesouro IGPM+ com Juros Semestrais"
        elif tesouro_type == "2":
            argumento = "Tesouro Selic"
        elif tesouro_type == "3":
            argumento = "Tesouro IPCA+"
        elif tesouro_type == "4":
            argumento = "Tesouro IPCA+ com Juros Semestrais"
        elif tesouro_type == "5":
            argumento = "Tesouro Prefixado com Juros Semestrais"
        elif tesouro_type == "6":
            argumento = "Tesouro Prefixado"
        else: 
            argumento = "Tesouro Selic"
        print(tesouro_type, argumento)

        URI = "mongodb://localhost:27017/"
        client = MongoClient(URI)
        db = client["tfg-database"]
        collection = db["precoTaxa"]
        dados = collection.find({"Tipo Titulo" : argumento })
        result = []
        for data in dados:
            result.append(data)
        return json.loads(json_util.dumps(result))
