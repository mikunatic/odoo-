from odoo import fields, models


class Rubric(models.Model):
    _name = 'rubric'
    _rec_name = 'code'

    code = fields.Integer("Código")
    description = fields.Char("Descrição")