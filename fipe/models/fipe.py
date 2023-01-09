import json

import requests

from odoo import models, fields


class Fipe(models.Model):
    _name = 'fipe'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Tabela Fipe'
    _rec_name = 'name'

    name = fields.Char('Nome', required=True)
    carro_id = fields.Integer('Modelo', required=True)
    marca_id = fields.Integer('Marca_id', required=True)
    marca = fields.Char('Marca', required=True)
    ano = fields.Integer('Ano', required=True)
    combustivel = fields.Char('Combustível')
    codigo_fipe = fields.Char('Código Fipe')
    pachave_ids = fields.Many2many(
        'pachave',
        string='Palavra Chave',
        relation='pachave_fipe_rel'
    )
    product_ids = fields.Many2many(
        'product.template',
        string='Peças'
    )

    _sql_constraints = [('name_unique', 'UNIQUE(Nome)', 'The name must be unique')]

    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s / %s " % (record.name, record.ano)
            result.append((record.id, rec_name))
        return result

    def testeFunc(self):
        f = open("error.txt", "w")

        mesesAno = {"janeiro": 1,
                    "fevereiro": 2,
                    "março": 3,
                    "abril": 4,
                    "maio": 5,
                    "junho": 6,
                    "julho": 7,
                    "agosto": 8,
                    "setembro": 9,
                    "outubro": 10,
                    "novembro": 11,
                    "dezembro": 12}
        urlRef = "http://veiculos.fipe.org.br/api/veiculos/ConsultarTabelaDeReferencia"
        requestRef = requests.post(urlRef)
        referencia = json.loads(requestRef.text)
        mesRef = mesesAno[str(referencia[0]["Mes"]).split("/", 1)[0]]
        anoRef = str(referencia[0]["Mes"]).split("/", 1)[1]

        codRef = referencia[0]["Codigo"]

        url = "http://veiculos.fipe.org.br/api/veiculos/ConsultarMarcas"
        body = dict(codigoTabelaReferencia=codRef, codigoTipoVeiculo=1)
        request = requests.post(url, headers={"codigoTabelaReferencia": str(codRef), "codigoTipoVeiculo": "1"},
                                data=body)

        data = json.loads(request.text)

        for rec in data:
            codigoMarca = rec['Value']
            urlMarcas = "http://veiculos.fipe.org.br/api/veiculos/ConsultarModelos"
            bodyMarcas = dict(codigoTabelaReferencia=codRef, codigoTipoVeiculo=1, codigoMarca=codigoMarca)
            requestMarca = requests.post(urlMarcas,
                                         headers={"codigoTabelaReferencia": str(codRef), "codigoTipoVeiculo": "1"},
                                         data=bodyMarcas)
            try:
                dataMarcas = json.loads(requestMarca.text)
            except json.decoder.JSONDecodeError:
                print('File is empty')
                print(request.text)
                f.write(urlMarcas)
                continue
            for marca in dataMarcas["Modelos"]:
                codigoModelo = marca['Value']
                urlAnoModelo = "http://veiculos.fipe.org.br/api/veiculos/ConsultarAnoModelo"
                bodyAnoModelo = dict(codigoTabelaReferencia=codRef, codigoTipoVeiculo=1, codigoMarca=codigoMarca,
                                     codigoModelo=codigoModelo)
                requestModelo = requests.post(urlAnoModelo,
                                              headers={"codigoTabelaReferencia": str(codRef), "codigoTipoVeiculo": "1"},
                                              data=bodyAnoModelo)
                try:
                    dataModelo = json.loads(requestModelo.text)
                except json.decoder.JSONDecodeError:
                    print('File is empty')
                    print(request.text)
                    f.write(urlAnoModelo)
                    continue
                for marcaAno in dataModelo:
                    tipo = str(marcaAno['Value']).split("-", 2)[1]
                    anoMarca = marcaAno['Value'].split("-", 2)[0] if int(marcaAno['Value'].split("-", 2)[0]) <= (
                                int(anoRef) + 1) else int(anoRef)
                    if int(anoMarca) < int(anoRef):
                        continue
                    urlValor = "http://veiculos.fipe.org.br/api/veiculos/ConsultarValorComTodosParametros"
                    bodyValor = dict(codigoTabelaReferencia=codRef, codigoTipoVeiculo=1, codigoMarca=codigoMarca,
                                     ano=anoMarca,
                                     codigoTipoCombustivel=tipo, anoModelo=anoMarca,
                                     codigoModelo=codigoModelo, tipoConsulta="tradicional")
                    requestValor = requests.post(urlValor, headers={"codigoTabelaReferencia": str(codRef),
                                                                    "codigoTipoVeiculo": "1"}, data=bodyValor)
                    try:
                        dataValor = json.loads(requestValor.text)
                        if dataValor.get('codigo') == '0':
                            continue
                        fipe_obj = self.search(
                            [('ano', '=', anoMarca), ('carro_id', '=', codigoModelo),
                             ('marca', '=', dataValor.get('Marca')), ('combustivel', '=', dataValor.get('Combustivel')),
                             ('codigo_fipe', '=', dataValor.get('CodigoFipe'))], limit=1)
                    except json.decoder.JSONDecodeError:
                        print('File is empty')
                        print(request.text)
                        f.write(urlValor)
                        continue

                    if not fipe_obj:
                        print(dataValor.get('Modelo'))
                        vals_list = {
                            'name': dataValor.get('Modelo'),
                            'carro_id': codigoModelo,
                            'marca_id': rec['Value'],
                            'marca': dataValor.get('Marca'),
                            'ano': anoRef,
                            'combustivel': dataValor.get('Combustivel'),
                            'codigo_fipe': dataValor.get('CodigoFipe')
                        }
                        self.create(vals_list)

        f.close()

    # def create(self, vals_list):
    #     if self.search([('name', '=like', vals_list.get("name"))]):
    #         return
    #     else:
    #         return super(Fipe, self).create(vals_list=vals_list)
