from odoo import fields, models


class Banco(models.Model):
    _name = "bank_cheque"
    _description = "All banks in FEBRABAN relation"
    _rec_name = 'name'

    name = fields.Char(
        'Banco',
        required=True
    )
    site = fields.Char(
        'Site',
        required=True
    )
    cod = fields.Integer(
        'Código',
        required=True
    )

    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s - %s " % (record.cod, record.name)
            result.append((record.id, rec_name))
        return result
