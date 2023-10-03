from odoo import fields, models, api


class HourMove(models.Model):
    _name = 'hour.move'

    # hour_move

    name = fields.Char('')
    operation_type = fields.Selection([('debito','Debito'),('credito','Credito')])

    def name_get(self):# rec_name para mostrar o tipo de operação
        return [(rec.id, rec.name + " / " + rec.operation_type) for rec in self]