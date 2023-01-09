from odoo import api, models, fields


class AccountFiscalPosition(models.Model):
    _inherit = 'account.move.line'

    @api.model_create_multi
    def create(self, vals_list):
        if vals_list and 'price_unit' in vals_list[0]:
            if len(vals_list[0]) < 50:
                return super(AccountFiscalPosition, self).create(vals_list)
            vals_remove = []
            vals_list[0]['credit'] = vals_list[0]['price_total'] = vals_list[0]['price_subtotal'] = vals_list[0][
                'price_unit']
            vals_list[0]['amount_currency'] = vals_list[0]['balance'] = -1 * vals_list[0]['price_unit']
            if vals_list:
                for line_tax in vals_list:
                    word_split = line_tax['name']
                    if word_split in ["COFINS Saida", "PIS Saida", "ICMS Saida"]:
                        vals_remove.append(line_tax)
                for line_tax in vals_remove:
                    vals_list.remove(line_tax)
                balance_total = 0
                for line_tax in vals_list:
                    if line_tax['credit'] > 0:
                        balance_total += line_tax['credit']
                    elif line_tax['name'] in ['ICMS Saida Subist', 'ICMS Saida FCP', "ICMS Saida"]:
                        line_tax['credit'] = line_tax['debit']
                        line_tax['debit'] = 0
                        line_tax['amount_currency'] = -1 * line_tax['amount_currency']
                        line_tax['balance'] = -1 * line_tax['balance']
                        balance_total += line_tax['credit']
                vals_list[-1]['price_unit'] = balance_total * -1
                vals_list[-1]['debit'] = balance_total
                vals_list[-1]['amount_currency'] = balance_total
        elif vals_list:
            if vals_list[0]['name'] in ['PIS Saida', 'COFINS Saida', 'ICMS Saida']:
                vals_list[0]['credit'] = 0.0
        return super(AccountFiscalPosition, self).create(vals_list)
