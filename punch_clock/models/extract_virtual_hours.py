from odoo import fields, models, api


class ExtractVirtualHours(models.Model):
    _name = 'extract.virtual.hours'

    # extract_virtual_hours

    time = fields.Char()
    day = fields.Date()
    employee_id = fields.Many2one('hr.employee')
    hour_move_id = fields.Many2one('hour.move')