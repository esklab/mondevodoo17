from odoo import models, fields, api
from datetime import timedelta, date
import logging

_logger = logging.getLogger(__name__)

class HrContract(models.Model):
    _inherit = 'hr.contract'

    show_salary_details = fields.Boolean(string="Show Salary Details")
    type_agent_id = fields.Many2one('hr.type.agent', string="Type d'agent")
    classe_id = fields.Many2one('hr.classe', string='Classe', domain="[('id', 'in', available_classe_ids)]")
    echelon_id = fields.Many2one('hr.echelon', string='Echelon', domain="[('id', 'in', available_echelon_ids)]")
    montant = fields.Float(string='Montant', compute='_compute_montant')

    available_classe_ids = fields.Many2many('hr.classe', compute='_compute_available_classe_ids')
    available_echelon_ids = fields.Many2many('hr.echelon', compute='_compute_available_echelon_ids')

    contract_start_date = fields.Date(string='Contract Start Date')
    last_promotion_date = fields.Date(string='Last Promotion Date')

    @api.depends('type_agent_id')
    def _compute_available_classe_ids(self):
        for record in self:
            if record.type_agent_id:
                if record.type_agent_id.name == 'Execution':
                    record.available_classe_ids = self.env['hr.classe'].search([('name', 'in', ['E1', 'E2', 'E3', 'E4'])])
                elif record.type_agent_id.name == 'Maitrise':
                    record.available_classe_ids = self.env['hr.classe'].search([('name', 'in', ['M1', 'M2'])])
                elif record.type_agent_id.name == 'Cadre ou Assimilés':
                    record.available_classe_ids = self.env['hr.classe'].search([('name', 'in', ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'])])
                else:
                    record.available_classe_ids = self.env['hr.classe'].search([])
            else:
                record.available_classe_ids = self.env['hr.classe'].search([])

    @api.depends('type_agent_id')
    def _compute_available_echelon_ids(self):
        for record in self:
            if record.type_agent_id:
                if record.type_agent_id.name == 'Execution':
                    record.available_echelon_ids = self.env['hr.echelon'].search([('name', 'in', ['1', '2', '3', '4', '5'])])
                elif record.type_agent_id.name == 'Maitrise':
                    record.available_echelon_ids = self.env['hr.echelon'].search([('name', 'in', ['1', '2', '3', '4', '5'])])
                elif record.type_agent_id.name == 'Cadre ou Assimilés':
                    record.available_echelon_ids = self.env['hr.echelon'].search([('name', 'in', ['1', '2', '3', '4', '5', '6', '7', '8', '9'])])
                else:
                    record.available_echelon_ids = self.env['hr.echelon'].search([])
            else:
                record.available_echelon_ids = self.env['hr.echelon'].search([])

    @api.onchange('type_agent_id')
    def _onchange_type_agent(self):
        self.classe_id = False
        self.echelon_id = False

    @api.onchange('show_salary_details')
    def _onchange_show_salary_details(self):
        self.type_agent_id = False
        self.classe_id = False
        self.echelon_id = False
        self.wage = False

    @api.depends('type_agent_id', 'classe_id', 'echelon_id')
    def _compute_montant(self):
        for record in self:
            salary = self.env['hr.salary'].search([
                ('type_agent_id', '=', record.type_agent_id.id),
                ('classe_id', '=', record.classe_id.id),
                ('echelon_id', '=', record.echelon_id.id)
            ], limit=1)
            if salary:
                record.montant = salary.montant
                record.wage = salary.montant
            else:
                record.montant = 0.0
                record.wage = 0.0

    def promote_to_next_echelon(self):
        echelon_names = [e.name for e in self.env['hr.echelon'].search([])]
        classe_names = [c.name for c in self.env['hr.classe'].search([])]

        for record in self:
            if not record.contract_start_date:
                _logger.info('No contract start date found.')
                continue

            # Check if it's been 2 years since the last promotion
            if record.last_promotion_date:
                next_promotion_date = record.last_promotion_date + timedelta(days=2*365)
            else:
                next_promotion_date = record.contract_start_date + timedelta(days=2*365)

            if fields.Date.today() < next_promotion_date:
                _logger.info('Not eligible for promotion yet. Next promotion date: %s', next_promotion_date)
                continue

            if record.echelon_id and record.classe_id:
                current_echelon_index = echelon_names.index(record.echelon_id.name)
                next_echelon_index = current_echelon_index + 1

                if next_echelon_index < len(echelon_names):
                    next_echelon = self.env['hr.echelon'].search([('name', '=', echelon_names[next_echelon_index])], limit=1)
                    if next_echelon:
                        record.echelon_id = next_echelon.id
                        record.last_promotion_date = fields.Date.today()
                        _logger.info('Promoted to next echelon: %s', next_echelon.name)
                    else:
                        _logger.info('No higher echelon available for promotion.')
                else:
                    current_classe_index = classe_names.index(record.classe_id.name)
                    next_classe_index = current_classe_index + 1

                    if next_classe_index < len(classe_names):
                        next_classe = self.env['hr.classe'].search([('name', '=', classe_names[next_classe_index])], limit=1)
                        if next_classe:
                            record.classe_id = next_classe.id
                            record.echelon_id = self.env['hr.echelon'].search([('name', '=', '1')], limit=1).id
                            record.last_promotion_date = fields.Date.today()
                            _logger.info('Promoted to next classe: %s, reset to echelon 1', next_classe.name)
                        else:
                            _logger.info('No higher classe available for promotion.')
                    else:
                        _logger.info('No higher classe available for promotion.')
            else:
                _logger.info('No echelon or classe found for promotion.')

    def check_and_promote_employees(self):
        contracts = self.search([])
        for contract in contracts:
            contract.promote_to_next_echelon()

class ModuleNameInit(models.Model):
    _name = 'module.name.init'
    
    @api.model
    def _create_cron_jobs(self):
        existing_cron = self.env['ir.cron'].search([('name', '=', 'Check and Promote Employees')])
        if not existing_cron:
            self.env['ir.cron'].create({
                'name': 'Check and Promote Employees',
                'interval_type': 'months',
                'interval_number': 1,
                'nextcall': fields.Datetime.now().replace(day=28, hour=23, minute=59, second=0, microsecond=0),
                'model_id': self.env['ir.model'].search([('model', '=', 'hr.contract')]).id,
                'code': 'model.check_and_promote_employees()',
                'numbercall': -1,
                'user_id': self.env.user.id,
                'priority': 5,
            })
            
    @api.model
    def init(self):
        self._create_cron_jobs()
        

    """def promote_to_next_echelon(self):
        for record in self:
            if record.echelon_id:
                next_echelon = self.env['hr.echelon'].search([
                    ('id', '>', record.echelon_id.id),
                    ('id', '<=', record.echelon_id.id + 1)
                ], limit=1, order='id asc')

                if next_echelon:
                    record.echelon_id = next_echelon.id
                    _logger.info('Promoted to next echelon: %s', next_echelon.name)
                else:
                    _logger.info('No higher echelon available for promotion.')

    @api.model
    def promote_all_to_next_echelon(self):
        contracts = self.search([('echelon_id', '!=', False)])
        for contract in contracts:
            contract.promote_to_next_echelon()"""
    
    """def promote_to_next_echelon(self):
        echelon_names = [e.name for e in self.env['hr.echelon'].search([])]
        classe_names = [c.name for c in self.env['hr.classe'].search([])]
        
        for record in self:
            if record.echelon_id and record.classe_id:
                current_echelon_index = echelon_names.index(record.echelon_id.name)
                next_echelon_index = current_echelon_index + 1

                if next_echelon_index < len(echelon_names):
                    next_echelon = self.env['hr.echelon'].search([('name', '=', echelon_names[next_echelon_index])], limit=1)
                    if next_echelon:
                        record.echelon_id = next_echelon.id
                        _logger.info('Promoted to next echelon: %s', next_echelon.name)
                    else:
                        _logger.info('No higher echelon available for promotion.')
                else:
                    current_classe_index = classe_names.index(record.classe_id.name)
                    next_classe_index = current_classe_index + 1

                    if next_classe_index < len(classe_names):
                        next_classe = self.env['hr.classe'].search([('name', '=', classe_names[next_classe_index])], limit=1)
                        if next_classe:
                            record.classe_id = next_classe.id
                            record.echelon_id = self.env['hr.echelon'].search([('name', '=', '1')], limit=1).id
                            _logger.info('Promoted to next classe: %s, reset to echelon 1', next_classe.name)
                        else:
                            _logger.info('No higher classe available for promotion.')
                    else:
                        _logger.info('No higher classe available for promotion.')
            else:
                _logger.info('No echelon or classe found for promotion.')

    @api.model
    def promote_all_to_next_echelon(self):
        contracts = self.search([('echelon_id', '!=', False), ('classe_id', '!=', False)])
        for contract in contracts:
            contract.promote_to_next_echelon()
        _logger.info('Promoted all contracts to the next echelon or classe.')

"""
