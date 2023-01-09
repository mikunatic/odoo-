# Copyright (C) 2013  Renato Lima - Akretion <renato.lima@akretion.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "l10n_br_fiscal.product.mixin"]
