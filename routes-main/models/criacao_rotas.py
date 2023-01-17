from odoo import models, api, fields


class CriacaoRotas(models.Model):
    _name = 'routes'
    _rec_name = "nome_rota"

    nome_rota = fields.Char('Nome da Rota')
