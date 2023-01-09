from odoo import fields, models, _
from odoo.exceptions import UserError


class AcountExtend(models.TransientModel):
    _name = 'account.extend'

    conta_origem_id = fields.Many2one(comodel_name='account.account', help="destination_account_id_origem",
                                      domain="[('user_type_id.type', 'in', ('receivable', 'payable'))]",
                                      required=True)
    banco_origem = fields.Many2one('res.partner.bank', string="Cliente/Fornecedor", required=True)
    partner_id = fields.Many2one('res.partner')
    partner_id_destino = fields.Many2one('res.partner')

    tipo_pagamento = fields.Selection([('inbound','Inbound'),('outbound','Outbound')])
    conta_destinatario = fields.Many2one(comodel_name='account.account', help="destination_account_id_destino",
                                         domain="[('user_type_id.type', 'in', ('receivable', 'payable'))]",
                                         required=True)
    banco_destinatario = fields.Many2one('res.partner.bank', string="Cliente/Fornecedor", required=True)

    currency_id = fields.Many2one('res.currency', string='Account Currency',
                                  help="Forces all moves for this account to have this account currency.", required=True)
    forma_pagamento = fields.Selection([('1','Cheque'),('2','Dinheiro')])
    cheque = fields.Many2one('cadastro.cheque')
    amount = fields.Monetary(currency_field='currency_id', required=True)
    journal_id = fields.Many2one('account.journal', required=True)
    journal_id_destino = fields.Many2one('account.journal', required=True)
    date = fields.Date("Data do pagamento", required=True)
    descricao = fields.Text("Descrição", compute="criardescricao", readonly=True)

    def botaopagar(self):
        vals = {'name': '/',
                'payment_type': 'outbound',
                'partner_type': 'customer',
                'partner_id': self.partner_id.id,
                'destination_account_id': self.conta_origem_id.id,
                'is_internal_transfer': False,
                'journal_id': self.journal_id.id,
                'payment_method_id': 1,
                'payment_token_id': False,
                'partner_bank_id': self.banco_origem.id,
                'auto_post': True,
                'amount': self.amount,
                'currency_id': self.currency_id.id,
                'check_amount_in_words': 'Zero Real',
                'date': self.date,
                'effective_date': False,
                'bank_reference': False,
                'cheque_reference': False,
                'ref': False,
                'edi_document_ids': [],
                'message_follower_ids': [],
                'activity_ids': [],
                'message_ids': [],
                } # lista de valores para criação do pagamento

        vals_dois = {'name': '/',
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': self.partner_id_destino.id,
                'destination_account_id': self.conta_destinatario.id,
                'is_internal_transfer': False,
                'journal_id': self.journal_id_destino.id,
                'payment_method_id': 1,
                'payment_token_id': False,
                'partner_bank_id': self.banco_destinatario.id,
                'auto_post': True,
                'amount': self.amount,
                'currency_id': self.currency_id.id,
                'check_amount_in_words': 'Zero Real',
                'date': self.date,
                'effective_date': False,
                'bank_reference': False,
                'cheque_reference': False,
                'ref': False,
                'edi_document_ids': [],
                'message_follower_ids': [],
                'activity_ids': [],
                'message_ids': [],
                } # lista de valores para criação do recebimento

        for rec in self: # erro personalizado caso o banco origem for igual ao destinatário, ou a quantia do pagamento for igual a zero
            if rec.banco_origem.id == rec.banco_destinatario.id or rec.amount == 0:
                raise UserError(_("Não é possível realizar transferências para a mesma conta ou sem valor"))


        self.env['account.payment'].create(vals) # cria o pagamento com os valores da primeira lista
        self.env['account.payment'].create(vals_dois) # cria o pagamento com os valores da segunda lista
        return self.env['ir.actions.act_window']._for_xml_id("account_extended.account_wiz_action") # mostra o wizard que efetua a postagem do pagamento

    def criardescricao(self): # função para criar a descrição personalizada
        for rec in self:
            if rec.currency_id.id == 6:
                cur = 'R$'
                rec.descricao = 'Pagamento de valor ' + cur + ' ' + str(rec.amount) + ', criado no dia ' + str(rec.date)
            elif rec.currency_id.id == 1:
                cur = 'Є'
                rec.descricao = 'Pagamento de valor ' + str(rec.amount) + ' ' + cur + ', criado no dia ' + str(rec.date)
            elif rec.currency_id.id == 2:
                cur = '$'
                rec.descricao = 'Pagamento de valor ' + cur + ' ' + str(rec.amount) + ', criado no dia ' + str(rec.date)

        # ESQUEÇAM TUDO!!!!!!!