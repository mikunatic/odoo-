from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    fipe_ids = fields.Many2many(
        'fipe',
        string="Veículos",
        relation='fipe_product_template_rel'
        # optional
    )
