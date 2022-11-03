from flask import Flask
from flask_restful import  Api
from flask_cors import CORS

from resources.tesouro import GetPrecoTaxa, GetTesouro, VendasTesouroDireto, PrecoTaxaTesouroDireto, OperacoesTesouroDireto

app = Flask(__name__)
api = Api(app)
cors = CORS(app)


# rotas de dados brutos
api.add_resource(VendasTesouroDireto, '/vendasTesouroDireto')
api.add_resource(PrecoTaxaTesouroDireto, '/precoTaxaTesouroDireto')
api.add_resource(OperacoesTesouroDireto, '/operacoesTesouroDireto')

# Rotas de dados filtrados
api.add_resource(GetTesouro, '/getTesouro')
api.add_resource(GetPrecoTaxa, '/getPrecoTaxa')


if __name__ == '__main__':
    app.run(debug=True)