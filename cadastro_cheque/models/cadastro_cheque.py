from odoo import fields, models, api


class CadastroCheque(models.Model):
    _name = 'cadastro.cheque'
    _rec_name = 'numero_cheque'

    numero_cheque = fields.Char(string="Número de Cheque", required=True)
    codigo_barra = fields.Char(string="Código de Barras", required=True)
    bank_cheque = fields.Many2one(
        "bank_cheque",
        required=True,
        tracking=True
    )
    agencia = fields.Char("Agência")
    tipo_cheque_id = fields.Selection(
        [
            ('5', 'Comum'),
            ('6', 'Bancário'),
            ('7', 'Salário'),
            ('8', 'Administrativo'),
            ('9', 'CPMF')
        ], default='5'
    )
    conta = fields.Many2one('account.account', default=25, readonly=True)
    data_cadastro = fields.Date("Data de Cadastro", required=True)
    currency_id = fields.Many2one('res.currency', string='Account Currency',
                                  required=True)
    valor = fields.Monetary(currency_field='currency_id', required=True)
    valor_extenso = fields.Char("Valor por extenso")
    account_cheque = fields.Char("Conta Bancária")
    terceiro = fields.Selection([('1','Sim'),('2','Não')], string="Cheque de Terceiro?", default='2')
    terceiro_nome = fields.Char("Nome do Terceiro")
    terceiro_cpf = fields.Char("CPF do Terceiro")
    terceiro_endereco = fields.Char("Endereço do Terceiro")
    descricao = fields.Text("Descrição", compute="criardescricao", readonly=True)

    @api.onchange("codigo_barra")
    def on_change_barcode(self):
        for rec in self:
            if rec.codigo_barra and len(rec.codigo_barra) == 34:
                rec.bank_cheque = rec.env['bank_cheque'].sudo().search([('cod', 'in', [rec.codigo_barra[1:4]])])
                rec.agencia = rec.codigo_barra[4:8]
                rec.numero_cheque = rec.codigo_barra[13:19]
                rec.account_cheque = rec.codigo_barra[25:32]
            else:
                rec.codigo_barra = ""

    @api.onchange("valor")
    def on_change_value_code(self):
        currency_id = self.env['res.currency'].browse(self.env.company.currency_id.id)
        for rec in self:
            text_amount = currency_id.amount_to_text(self.valor)
            if text_amount.__eq__("Um Real"):
                rec.valor_extenso = text_amount
            else:
                rec.valor_extenso = text_amount.replace("Real", "Reais")

    def postarcheque(self):
        vals_credito_cheque = {'name': '/',
                      'payment_type': 'outbound',
                      'partner_type': 'customer',
                      'partner_id': False,
                      'destination_account_id': 25,
                      'is_internal_transfer': False,
                      'journal_id': 13,
                      'payment_method_id': 1,
                      'payment_token_id': False,
                      'partner_bank_id': 11,
                      'amount': self.valor,
                      'currency_id': 6,
                      'check_amount_in_words': self.valor_extenso,
                      'date': self.data_cadastro,
                      'effective_date': False,
                      'bank_reference': False,
                      'cheque_reference': False,
                      'ref': False,
                      'edi_document_ids': [],
                      'message_follower_ids': [],
                      'activity_ids': [],
                      'message_ids': [],
                      }

        vals_debito_cheque = {'name': '/',
                        'payment_type': 'inbound',
                        'partner_type': 'customer',
                        'partner_id': False,
                        'destination_account_id': 25,
                        'is_internal_transfer': False,
                        'journal_id': 7,
                        'payment_method_id': 1,
                        'payment_token_id': False,
                        'partner_bank_id': 10,
                        'amount': self.valor,
                        'currency_id': self.currency_id.id,
                        'check_amount_in_words': self.valor_extenso,
                        'date': self.data_cadastro,
                        'effective_date': False,
                        'bank_reference': False,
                        'cheque_reference': False,
                        'ref': False,
                        'edi_document_ids': [],
                        'message_follower_ids': [],
                        'activity_ids': [],
                        'message_ids': [],
                        }
        self.env['account.payment'].create(vals_credito_cheque)
        self.env['account.payment'].create(vals_debito_cheque)

        return self.env['ir.actions.act_window']._for_xml_id("cadastro_cheque.cheque_wiz_action") # mostra o wizard que efetua a postagem do pagamento

    def criardescricao(self):  # função para criar a descrição personalizada
        for rec in self:
            if rec.currency_id.id == 6:
                cur = 'R$'
                rec.descricao = 'Cheque de valor ' + cur + ' ' + str(rec.valor) + ', criado no dia ' + str(
                    rec.data_cadastro)
            elif rec.currency_id.id == 1:
                cur = 'Є'
                rec.descricao = 'Cheque de valor ' + str(rec.valor) + ' ' + cur + ', criado no dia ' + str(
                    rec.data_cadastro)
            elif rec.currency_id.id == 2:
                cur = '$'
                rec.descricao = 'Cheque de valor ' + cur + ' ' + str(rec.valor) + ', criado no dia ' + str(
                    rec.data_cadastro)