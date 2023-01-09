from odoo import models


class SaleOrderLine(models.Model):
    _name = "product.product"
    _inherit = _name

    def name_get(self):
        rtn = super(SaleOrderLine, self).name_get()
        result = []
        for rec in self:
            rec_name = "%s" % rec.default_code
            result.append((rec.id, rec_name))
        rtn = result
        return rtn
