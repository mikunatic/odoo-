from odoo import fields, models


class VirtualBank(models.Model):
    _name = 'virtual.bank'

    date = fields.Date("Dia")
    hours = fields.Char("Horas")
    employee_id = fields.Many2one('hr.employee')
    move_type = fields.Selection([('credit','Crédito'),('debit','Débito')])
    events_id = fields.Many2one('event')