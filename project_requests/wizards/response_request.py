import datetime
from datetime import timedelta

from odoo import models, fields
from odoo.exceptions import UserError


class ResponseRequest(models.TransientModel):
    _name = "response_request"
    _description = "Resposta da Requisição"

    response = fields.Text(
        "Resposta",
        required=True
    )

    project_request_id = fields.Many2one(
        'project_request',
        string='Project Request ID',
        required=True,
        readonly=True
    )

    def send_response(self):
        if self.env.user.email is False:
            raise UserError("Não foi possível registrar a mensagem, configure o endereço de e-mail do remetente.")
        vals = {
            'author_id': self.env.user.partner_id.id,
            'author_guest_id': False,
            'email_from': '"Administrator" <' + self.env.user.email + '>',
            'model': 'project_request',
            'res_id': self.project_request_id.id,
            'body': 'Resposta : <br/>' + self.response,
            'subject': False,
            'message_type': 'comment',
            'parent_id': self.project_request_id.message_ids.ids[-1],
            'subtype_id': 1,
            'partner_ids': [],
            'add_sign': True,
            'record_name': self.project_request_id.display_name,
            'attachment_ids': []
        }
        self.env["mail.message"].create(vals)

        days_update_due_date = self.update_due_date(last_update=self.project_request_id.update_date)
        print(days_update_due_date)
        vals = {
            "update_date": fields.datetime.today(),
            "status": "andamento"
        }
        if days_update_due_date > 0:
            vals["due_date"] = self.validate_answer(count=days_update_due_date,
                                                    due_date=self.project_request_id.due_date)
            self.env["mail.message"].create({
                'author_id': self.env.user.partner_id.id,
                'author_guest_id': False,
                'email_from': '"Administrator" <' + self.env.user.email + '>',
                'model': 'project_request',
                'res_id': self.project_request_id.id,
                'body': 'Atualização da Data de Vencimento da Requisição : <br/> Após o retorno do solicitante foi '
                        'adicinado ' + str(days_update_due_date) + ' ao prazo de atendimento.',
                'subject': False,
                'message_type': 'comment',
                'parent_id': self.project_request_id.message_ids.ids[-1],
                'subtype_id': 1,
                'partner_ids': [],
                'add_sign': True,
                'record_name': self.project_request_id.display_name,
                'attachment_ids': []
            })
        self.project_request_id.write(vals)

    def update_due_date(self, last_update, at_moment=datetime.date.today()):
        print(at_moment)
        print(last_update)
        return (at_moment - last_update).days

    # Retornar a nova data maxima de atendimento do chamado
    def validate_answer(self, count, due_date):
        # Atribui o dia de abertura da requisição
        current = due_date
        # Atribui o dia de abertura da requisição
        while 0 < count:
            # Verifica se o dia é final de semana
            if current.weekday() in (5, 6):
                due_date += timedelta(days=1)
            due_date += timedelta(days=1)
            current += timedelta(days=1)
            count -= 1
        return due_date
