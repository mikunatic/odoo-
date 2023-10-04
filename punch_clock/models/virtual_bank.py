from odoo import fields, models


class VirtualBank(models.Model):
    _name = 'virtual.bank'

    date = fields.Date("Dia")
    hours = fields.Char("Horas")
    employee_id = fields.Many2one('hr.employee')
    movement_type = fields.Reference([('credit.virtual.bank', 'Crédito'),
                                      ('debit.virtual.bank', 'Débito')],
                                     string="Movimentação")
    seconds = fields.Integer()