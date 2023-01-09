from odoo import models, fields, api

from odoo.tools.float_utils import float_round as round


class AccountTax(models.Model):
    _inherit = "account.tax"

    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None, is_refund=False,
                    handle_price_include=True):

        rec = super(AccountTax, self).compute_all(price_unit, currency, quantity, product, partner, is_refund,
                                                  handle_price_include)
        return rec
