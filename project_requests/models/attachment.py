from odoo import models, api, fields


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    recurring_id = fields.Many2one(comodel_name="project_request.recurring")
