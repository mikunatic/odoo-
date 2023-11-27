from odoo import fields, models, api


class VirtualHours(models.Model):
    _name = 'extract.virtual.hours'
    _rec_name = 'employee_id'
    _order = 'id desc'

    date = fields.Date("Data")
    employee_id = fields.Many2one('hr.employee', string="Funcionário")
    hours = fields.Char("Horas", required=True)
    movement_type = fields.Reference([('credit.virtual.bank', 'Crédito'),
                                      ('debit.virtual.bank', 'Débito')],
                                     string='Movimentação')
    reference_bool = fields.Boolean()
    balance = fields.Char("Saldo de Horas")
    balance_in_seconds = fields.Integer()

