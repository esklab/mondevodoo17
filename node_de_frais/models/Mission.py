from odoo import fields, models, api


class Mission(models.Model):
    _inherit = 'project.task'
    frais_ids = fields.Many2many('hr.expense', string='Notes de frais')
    personne_assigne = fields.Many2one('hr.employee', string='Personne assignée')
