from odoo import fields, models


class Company(models.Model):
    _name = 'employee.company'

    name = fields.Char("Nome")
    cnpj = fields.Char("CNPJ")
    city = fields.Char("Cidade")
    inscricao_estadual = fields.Char("Inscrição Estadual")
