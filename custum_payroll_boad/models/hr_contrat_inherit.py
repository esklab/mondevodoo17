from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class HrContract(models.Model):
    _inherit = 'hr.contract'

    show_salary_details = fields.Boolean(string="Show Salary Details")
    type_salary_id = fields.Many2one('hr.type.salary', string='Type de Salaire')
    rang_id = fields.Many2one('hr.rang', string='Rang', domain="[('id', 'in', available_rang_ids)]")
    echelon_id = fields.Many2one('hr.echelon', string='Echelon', domain="[('id', 'in', available_echelon_ids)]")
    montant = fields.Float(string='Montant', compute='_compute_montant')
    
    available_rang_ids = fields.Many2many('hr.rang', compute='_compute_available_rang_ids')
    available_echelon_ids = fields.Many2many('hr.echelon', compute='_compute_available_echelon_ids')

    @api.depends('type_salary_id')
    def _compute_available_rang_ids(self):
        for record in self:
            if record.type_salary_id:
                if record.type_salary_id.name == 'CATEGORIES':
                    record.available_rang_ids = self.env['hr.rang'].search([('name', 'in', ['1ER', '2EME', '3EME', '4EME', '5EME', '6EME', '7EME'])])
                elif record.type_salary_id.name == 'CLASSES':
                    record.available_rang_ids = self.env['hr.rang'].search([('name', 'in', ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'])])
                else:
                    record.available_rang_ids = self.env['hr.rang'].search([])
            else:
                record.available_rang_ids = self.env['hr.rang'].search([])

    @api.depends('type_salary_id', 'rang_id')
    def _compute_available_echelon_ids(self):
        for record in self:
            if record.type_salary_id and record.rang_id:
                if record.type_salary_id.name == 'CATEGORIES' and record.rang_id.name == '1ER':
                    record.available_echelon_ids = self.env['hr.echelon'].search([('name', 'in', ['A'])])
                elif record.type_salary_id.name == 'CLASSES' and record.rang_id.name in ['I', 'II', 'III']:
                    record.available_echelon_ids = self.env['hr.echelon'].search([('name', 'in', ['A','B'])])
                else:
                    record.available_echelon_ids = self.env['hr.echelon'].search([('name', 'in', ['A', 'B', 'C'])])
            else:
                record.available_echelon_ids = self.env['hr.echelon'].search([])

    @api.onchange('type_salary_id')
    def _onchange_type_salary(self):
        self.rang_id = False
        self.echelon_id = False

    @api.onchange('show_salary_details')
    def _onchange_show_salary_details(self):
        self.type_salary_id = False
        self.rang_id = False
        self.echelon_id = False
        self.wage = False

    @api.depends('type_salary_id', 'rang_id', 'echelon_id')
    def _compute_montant(self):
        for record in self:
            if record.type_salary_id:
                echelon_name = record.echelon_id.name
                rang_name = record.rang_id.name
                salary = self.env['hr.salary'].search([
                    ('type_salary_id', '=', record.type_salary_id.id),
                    ('rang_id.name', '=', rang_name),
                    ('echelon_id.name', '=', echelon_name)
                ], limit=1)
                
                if salary:
                    record.montant = salary.montant
                    record.wage = salary.montant
                else:
                    record.montant = 0.0
                    record.wage = 0.0
            else:
                record.montant = 0.0
