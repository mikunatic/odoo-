from odoo import api, models, fields


class OperationLine(models.Model):
    _name = "l10n_br_fiscal.operation.line"
    _inherit = _name

    computed_field = fields.Boolean(
        string="Computed Field",
        compute="_get_operation_line_id"
    )

    ncm_ids = fields.Many2many(
        comodel_name="l10n_br_fiscal.ncm",
        relation="operation_line_ncm_rel",
        string="NCMs",
        readonly=False
    )

    cest_ids = fields.Many2many(
        comodel_name="l10n_br_fiscal.cest",
        relation="fiscal_extension_cest_rel",
        string="CESTs",
        readonly=False
    )

    def _get_operation_line_id(self):
        tax_ids = self.tax_definition_ids.tax_id.ids
        operation_line_id = self.id
        tax_definition_obj = self.env['l10n_br_fiscal.tax'].search([('id', 'in', tax_ids)])
        for record in tax_definition_obj:
            record.write({'operation_line_receiver': operation_line_id})
        self.computed_field = True
