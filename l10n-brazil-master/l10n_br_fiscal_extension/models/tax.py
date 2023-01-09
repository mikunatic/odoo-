from odoo import models, fields, api


class Tax(models.Model):
    _name = "l10n_br_fiscal.tax"
    _inherit = _name

    add_base_tax = fields.Many2many(
        string="Tax add Base",
        comodel_name="l10n_br_fiscal.tax.definition",
        domain="[('fiscal_operation_line_id', '=', operation_line_receiver), ('tax_id', '!=', tax_id)]"
    )

    operation_line_receiver = fields.Integer(
        string="Operation Line"
    )

    tax_id = fields.Integer(
        string="Tax id",
        compute="_get_tax_id"
    )

    def _compute_tax_base(self, tax, tax_dict, **kwargs):
        icms_st_tax_id = self.search([('name', 'ilike', 'ICMS MVA')], limit=1).tax_group_id.id
        res = super(Tax, self)._compute_tax_base(tax, tax_dict, **kwargs)
        # Verifica a necessidade de alterar a base de calculo
        if tax.add_base_tax:
            base_value = 0.0
            total_price = kwargs.get('price_unit') * kwargs.get('quantity')
            base_value += total_price
            for new_tax in tax.add_base_tax:
                if new_tax.tax_id.tax_group_id.id.__eq__(9):
                    for alter_tax in new_tax.tax_id.add_base_tax:
                        base_value += (total_price * (alter_tax.tax_id.percent_amount / 100))
                    base_value += (base_value * (new_tax.tax_id.icmsst_mva_percent / 100))
                else:
                    base_value += (total_price * (new_tax.tax_id.percent_amount / 100))
            if tax.tax_group_id.id.__eq__(9):
                base_value += (base_value * (tax.icmsst_mva_percent / 100))
            res["base"] = base_value
        return res


    def _get_tax_id(self):
        self.tax_id = self.id