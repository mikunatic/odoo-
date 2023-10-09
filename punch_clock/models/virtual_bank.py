from odoo import fields, models


class VirtualBank(models.Model):
    _name = 'virtual.bank'

    date = fields.Date("Dia", required=True)
    hours = fields.Char("Horas", required=True)
    employee_id = fields.Many2one('hr.employee', string="Funcionário", required=True)
    movement_type = fields.Reference([('credit.virtual.bank', 'Crédito'),
                                      ('debit.virtual.bank', 'Débito')],
                                     string="Movimentação", required=True)
    seconds = fields.Integer()
    reference_bool = fields.Boolean()