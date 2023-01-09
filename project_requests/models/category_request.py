from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class CategoryRequest(models.Model):
    _name = "category_request"
    _description = "Categoria da Requisição"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char(
        string="Descrição",
        tracking=True,
        required=True
    )
    due_date = fields.Integer(
        string="Prazo",
        tracking=True
    )
    parent_id = fields.Many2one(
        'category_request',
        'Categoria',
        index=True,
        ondelete='cascade',
        tracking=True
    )
    parent_path = fields.Char(
        index=True
    )
    child_id = fields.One2many(
        'category_request',
        'parent_id',
        'Categorias filho'
    )
    type = fields.Selection(
        [
            ('parent', 'Pai'),
            ('child', 'Filho')
        ],
        string="Tipo",
        required=True,
        default="parent"
    )
    status = fields.Selection(
        [
            ('Habilitado', 'Habilitado'),
            ('Desabilitado', 'Desabilitado')
        ],
        string="Tipo",
        required=True,
        default="Habilitado",
        tracking=True
    )
    department_id = fields.Many2one(
        "hr.department",
        string="Departamento",
        required=True,
        # readonly=True,
        default=lambda self: self.env["hr.employee"].search([("user_id", "=", self.env.uid)]).department_id
    )
    internal_request = fields.Boolean(
        string="Interno",
        default=False,
        tracking=True
    )
    has_client = fields.Boolean(
        string="Possui Cliente",
        default=False,
        tracking=True
    )

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError('Você não pode criar categorias recursivas.')

    def alter_state(self):
        if self.status.__eq__("Habilitado"):
            self.write({"status": "Desabilitado"})
        else:
            self.write({"status": "Habilitado"})

    def unlink(self):
        if self.type.__eq__("parent"):
            projects_requests_ids = self.env["project_request"].search([("category_parent_request_id", "=", self.id)])
            if len(projects_requests_ids.ids) > 0:
                raise UserError("Categoria já utilizada em " + str(
                    len(projects_requests_ids.ids)) + " requisição(s), não é possivel realizar a exclusão.")
        else:
            projects_requests_ids = self.env["project_request"].search([("category_child_request", "=", self.id)])
            if len(projects_requests_ids.ids) > 0:
                raise UserError("Sub-Categoria já utilizada em " + str(
                    len(projects_requests_ids.ids)) + " requisição(s), não é possivel realizar a exclusão.")
        return super(CategoryRequest, self).unlink()
