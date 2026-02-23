from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class HrTypeSalary(models.Model):
    _name = 'hr.type.salary'
    _description = 'Type of Salary'

    name = fields.Char(string='Type de Salaire', required=True)

class HrRang(models.Model):
    _name = 'hr.rang'
    _description = 'Rang'

    name = fields.Char(string='Rang', required=True)

class HrEchelon(models.Model):
    _name = 'hr.echelon'
    _description = 'Echelon'

    name = fields.Char(string='Echelon', required=True)

class HrSalary(models.Model):
    _name = 'hr.salary'
    _description = 'Salary Grid'

    type_salary_id = fields.Many2one('hr.type.salary', string='Type de Salaire', required=True)
    rang_id = fields.Many2one('hr.rang', string='Rang', required=True)
    echelon_id = fields.Many2one('hr.echelon', string='Echelon', required=True)
    points = fields.Float(string='Points')
    montant = fields.Float(string='Montant', compute='_compute_montant', store=True)

    @api.depends('points')
    def _compute_montant(self):
        for record in self:
            record.montant = record.points * 202.22
