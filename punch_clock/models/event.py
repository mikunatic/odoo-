from odoo import fields, models


class Event(models.Model):
    _name = 'event'
    _rec_name = 'description'

    description = fields.Char("Descrição")
    credit_debit = fields.Selection([('credit','Crédito'),('debit','Débito')], string="Débito/Crédito")
    measurement_unit = fields.Selection([('hours','Horas'),('days','Dias')], string="Unidade de Medida")
    number = fields.Integer(string="Número")