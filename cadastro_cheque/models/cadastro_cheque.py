from odoo import fields, models, api


class CadastroCheque(models.Model):
    _name = 'cadastro.cheque'

    numero_cheque = fields.Char(string="Número de Cheque", required=True)
    codigo_barra = fields.Char(string="Código de Barras", required=True)
    bank_id = fields.Many2one('res.partner.bank', string="Conta bancária", required=True)
    agencia = fields.Char("Agência")
    tipo_cheque_id = fields.Selection(
        [
            ('5', 'Comum'),
            ('6', 'Bancário'),
            ('7', 'Salário'),
            ('8', 'Administrativo'),
            ('9', 'CPMF')
        ]
    )
    conta = fields.Many2one('account.account', default=25, readonly=True)
    data_cadastro = fields.Date("Data de Cadastro")
    currency_id = fields.Many2one('res.currency', string='Account Currency',
                                  required=True)
    valor = fields.Monetary(currency_field='currency_id', required=True)
    valor_extenso = fields.Char("Valor por extenso", compute="_compute_check_amount_in_words")

    @api.depends('currency_id', 'valor')
    def _compute_check_amount_in_words(self):
        for pay in self:
            if pay.currency_id:
                pay.valor_extenso = pay.currency_id.valor_extenso(pay.valor)
            else:
                pay.valor_extenso = False
