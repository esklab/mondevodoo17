from odoo import models, fields,api,_
import logging

_logger = logging.getLogger(__name__)

class HrTypeAgent(models.Model):
    _name = 'hr.type.agent'
    _description = 'Type of Agent'

    name = fields.Char(string='Name', required=True)

class HrClasse(models.Model):
    _name = 'hr.classe'
    _description = 'Classe'

    name = fields.Char(string='Name', required=True)

class HrEchelon(models.Model):
    _name = 'hr.echelon'
    _description = 'Echelon'

    name = fields.Char(string='Name', required=True)

class HrSalary(models.Model):
    _name = 'hr.salary'
    _description = 'Salary Grid'

    type_agent_id = fields.Many2one('hr.type.agent', string='Type d\'agent', required=True)
    classe_id = fields.Many2one('hr.classe', string='Classe', required=True)
    echelon_id = fields.Many2one('hr.echelon', string='Echelon', required=True)
    montant = fields.Float(string='Montant')

   