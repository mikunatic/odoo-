from odoo import api, models, fields


class UpdateProjectStatus(models.TransientModel):
    _name = "update.project.status.wizard"

    status = fields.Selection([
        ('aberto', 'Aberto'),
        ('andamento', 'Em Andamento'),
        ('aguardando_resposta', 'Aguardando Resposta'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado')
    ], 'Status', required=True)

    response_problem = fields.Text(
        "Resposta / Solução",
        tracking=True
    )

    def save(self):
        self.env['project_request'].browse(self._context.get('active_ids')).alter_status(self.status)
