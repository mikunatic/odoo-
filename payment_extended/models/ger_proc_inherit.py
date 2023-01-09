from odoo import fields, models


class GerProcInherit(models.Model):
    _inherit = 'project_request'

    payment = fields.One2many(comodel_name='account.payment', inverse_name='gerproc', readonly=True)
