from odoo import fields, models, _,api
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
                                  help="Forces all moves for this account to have this account currency.", default=6)
    forma_pagamento = fields.Selection([('1','Cheque'),('2','Dinheiro'),('3','Lote'),('4','Devolução')], string="Forma de Pagamento")
    cheque = fields.Many2one('cadastro.cheque', domain="[('pagamentos','=',False)]")
    # domain = "['|',('pagamentos','=',False),('lote_ids','=',False)]" domain antigo do cheque
    valor_cheque = fields.Monetary(related="cheque.valor")
    lote_id = fields.Many2one('lote.cheque', domain="[('pagamento_ids','=',False)]")
    valor_lote = fields.Monetary(related="lote_id.valor_total")
    amount = fields.Monetary(currency_field='currency_id')
    journal_id = fields.Many2one('account.journal', required=True)
    journal_id_destino = fields.Many2one('account.journal', required=True)
    date = fields.Date("Data do pagamento", required=True)
    descricao = fields.Text("Descrição", compute="criardescricao", readonly=True)
    
    def botaopagar(self):
        for rec in self:
            if rec.forma_pagamento == '1':
                valor = rec.valor_cheque
            elif rec.forma_pagamento == '2':
                valor = rec.amount
            elif rec.forma_pagamento == '3':
                valor = rec.valor_lote
        vals_pagar = {'name': '/',
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
                      'currency_id': 6,
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
                      }
        vals_pagamento_com_cheque = {'name': '/',
                     'payment_type': 'outbound',
                     'partner_type': 'customer',
                     'partner_id': self.partner_id.id,
                     'destination_account_id': 25,  # account.account clientes circulante
                     'is_internal_transfer': False,
                     'journal_id': 7,
                     'payment_method_id': 1,
                     'payment_token_id': False,
                     'partner_bank_id': 10,
                     'auto_post': True,
                     'amount': self.valor_cheque,
                     'currency_id': 6,
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
                     'cheque_pagamento':self.cheque.id,
                    }
        if self.forma_pagamento == '3':
            for cheque in self.lote_id.cheque_ids:
                vals_pagamento_com_lote = {'name': '/',
                             'payment_type': 'outbound',
                             'partner_type': 'customer',
                             'partner_id': self.partner_id.id,
                             'destination_account_id': 25,  # account.account clientes circulante
                             'is_internal_transfer': False,
                             'journal_id': 7,
                             'payment_method_id': 1,
                             'payment_token_id': False,
                             'partner_bank_id': 10,
                             'auto_post': True,
                             'amount': cheque.valor,
                             'currency_id': 6,
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
                             'cheque_pagamento':cheque.id,
                             'lote_id': self.lote_id.id,
                            }

                vals_receber_com_lote = {'name': '/',
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
                                'amount': cheque.valor,
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
                                'cheque_pagamento': cheque.id,
                                'lote_id': self.lote_id.id,
                                }
                self.env['account.payment'].create(vals_pagamento_com_lote)  # cria o pagamento com os valores da primeira lista
                self.env['account.payment'].create(vals_receber_com_lote)
                pagamento = self.env['account.payment'].search([],order="id asc")
                description = self.env['account.extend'].search([],order="id asc")
                desc = description[-1].descricao
                pagamento[-1].action_post()
                pagamento[-2].action_post()
                vals_ger_proc = {'status': 'aberto',
                                 'private_message': 'public',
                                 'department_id': 4,  # required
                                 'user_requested_id': 1,
                                 'users_views_ids': [[6, False, []]],
                                 'department_views_ids': [[6, False, [1, 2, 3]]],
                                 'category_parent_request_id': 4,  # required
                                 'category_child_request': 5,  # required
                                 'boolean_client': False,
                                 'request_client_ids': [[6, False, []]],
                                 'description_problem': desc,  # required
                                 'my_requests': [[6, False, []]],
                                 'message_follower_ids': [],
                                 'activity_ids': [],
                                 'message_ids': [],
                                 }
                self.env['project_request'].create(vals_ger_proc)  # cria um gerproc com os dados passados na lista acima
                last_gp = self.env['project_request'].search([],order="id asc")  # pesquisa os gerprocs e ordena por id ascendente
                gpr = last_gp[-1]  # armazena na variavel gpr o último gerproc criado
                pagamento[-1].update({'gerproc': gpr.id})  # atualiza o campo gerproc, presente no account.payment, com o id do ultimo gerproc, no pagamento e recebimento
                pagamento[-2].update({'gerproc': gpr.id})

                return {
                    "type": "ir.actions.act_window",
                    "name": _("Project Request"),
                    "res_model": "project_request",
                    "domain": [("id", "=", gpr.id)],
                    "view_mode": "tree,form",
                    "context": self.env.context
                }
        vals_receber = {'name': '/',
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
                        'amount': valor,
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
                        'cheque_pagamento': self.cheque.id,
                        'lote_id': self.lote_id.id,
                        }
        vals_devolucao_out = {'name': '/',
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
                      'currency_id': 6,
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
                      }
        vals_devolucao_in = {'name': '/',
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
                      'currency_id': 6,
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
                      }
        for rec in self:
            if rec.forma_pagamento == '1':
                self.env['account.payment'].create(vals_pagamento_com_cheque)  # cria o pagamento com os valores da primeira lista
                self.env['account.payment'].create(vals_receber)
                return self.env['ir.actions.act_window']._for_xml_id("account_extended.account_wiz_action")  # mostra o wizard que efetua a postagem do pagamento
            elif rec.forma_pagamento == '2':
                self.env['account.payment'].create(vals_pagar)  # cria o pagamento com os valores da primeira lista
                self.env['account.payment'].create(vals_receber)
                return self.env['ir.actions.act_window']._for_xml_id("account_extended.account_wiz_action")  # mostra o wizard que efetua a postagem do pagamento
            elif rec.forma_pagamento == '4':
                self.env['account.payment'].create(vals_devolucao_out)
                self.env['account.payment'].create(vals_devolucao_in)
                return self.env['ir.actions.act_window']._for_xml_id("account_extended.account_wiz_action")
    @api.onchange("forma_pagamento")
    def onchange_cheque(self):
        if self.forma_pagamento == '1' or self.forma_pagamento == '3':
            self.banco_origem = 10
            self.conta_origem_id = 25
            self.journal_id = 7
        elif self.forma_pagamento == '2':
            self.banco_origem = False
            self.conta_origem_id = False
            self.journal_id = False

    def criardescricao(self): # função para criar a descrição personalizada
        for rec in self:
            if rec.forma_pagamento == '1':
                if rec.currency_id.id == 6:
                    cur = 'R$'
                    rec.descricao = 'Pagamento de valor ' + cur + ' ' + str(rec.valor_cheque) + ', criado no dia ' + str(rec.date)
                elif rec.currency_id.id == 1:
                    cur = 'Є'
                    rec.descricao = 'Pagamento de valor ' + str(rec.valor_cheque) + ' ' + cur + ', criado no dia ' + str(rec.date)
                elif rec.currency_id.id == 2:
                    cur = '$'
                    rec.descricao = 'Pagamento de valor ' + cur + ' ' + str(rec.rec.valor_cheque) + ', criado no dia ' + str(rec.date)
            elif rec.forma_pagamento == '2':
                if rec.currency_id.id == 6:
                    cur = 'R$'
                    rec.descricao = 'Pagamento de valor ' + cur + ' ' + str(rec.amount) + ', criado no dia ' + str(rec.date)
                elif rec.currency_id.id == 1:
                    cur = 'Є'
                    rec.descricao = 'Pagamento de valor ' + str(rec.amount) + ' ' + cur + ', criado no dia ' + str(rec.date)
                elif rec.currency_id.id == 2:
                    cur = '$'
                    rec.descricao = 'Pagamento de valor ' + cur + ' ' + str(rec.amount) + ', criado no dia ' + str(rec.date)
            elif rec.forma_pagamento == '3':
                if rec.currency_id.id == 6:
                    cur = 'R$'
                    rec.descricao = 'Pagamento de valor ' + cur + ' ' + str(rec.valor_lote) + ', criado no dia ' + str(rec.date)
                elif rec.currency_id.id == 1:
                    cur = 'Є'
                    rec.descricao = 'Pagamento de valor ' + str(rec.valor_lote) + ' ' + cur + ', criado no dia ' + str(rec.date)
                elif rec.currency_id.id == 2:
                    cur = '$'
                    rec.descricao = 'Pagamento de valor ' + cur + ' ' + str(rec.valor_lote) + ', criado no dia ' + str(rec.date)
        # ESQUEÇAM TUDO!!!!!!!