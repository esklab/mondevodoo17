from odoo import api, fields, models, SUPERUSER_ID
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

class HrPayslipExtended(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super(HrPayslipExtended, self).action_payslip_done()
        if self.employee_id:
            employee = self.employee_id
            # Créer l'allocation de congés pour cet employé spécifique
            leave_allocation = employee.create_leave_allocation(employee,2.5, 1, 'Allocation Mensuelles')
            _logger.info(f"Leave allocation created for employee {employee.name} with ID: {leave_allocation.id}")
        else:
            _logger.warning("No employee associated with the payslip.")
        return res

class HrLeaveAllocationExtended(models.Model):
    _inherit = 'hr.leave.allocation'

    number_of_days = fields.Float(string='Number of Days', readonly=False)
    number_of_days_display = fields.Float(string='Duration (days)', readonly=False)

class EmployeeLeaveAllocation(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def create_leave_allocation(self, employee, number_of_days, holiday_status_id, allocation_name, with_monthly_period=False):
        # Vérifiez si une période mensuelle est requise
        leave_allocation_vals = {
            'name': allocation_name,
            'holiday_status_id': holiday_status_id,
            'allocation_type': 'regular',
            'number_of_days': number_of_days,
            'holiday_type': 'employee',
            'employee_id': employee.id,
        }
        
        if with_monthly_period:
            # Période du premier au dernier jour du mois
            start_date = datetime.today().replace(day=1)
            end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)
            leave_allocation_vals.update({
                'date_from': start_date,
                'date_to': end_date,
            })

        return self.env['hr.leave.allocation'].create(leave_allocation_vals)
    
    def allocate_monthly_leave(self):
        employees = self.search([])
        for employee in employees:
            leave_allocation = self.create_leave_allocation(employee, 2.5, 1, 'Allocation Mensuelles')
            _logger.info(f"Leave allocation created for employee {employee.name} with ID: {leave_allocation.id}")

    def allocate_monthly_remote_day(self):
        employees = self.search([])
        for employee in employees:
            # Allocation avec période mensuelle
            leave_allocation = self.create_leave_allocation(employee, 2, 7, 'Allocation Mensuelle de Jours de Teletravail', with_monthly_period=True)
            _logger.info(f"Tele travail Days allocated for {employee.name} with ID: {leave_allocation.id}")

    old_children_number = fields.Integer(string='Ancien nombre d\'enfants', store=False, readonly=True)

    @api.model
    def create(self, vals):
        res = super(EmployeeLeaveAllocation, self).create(vals)
        if res.marital == 'single':
            res.allocate_bachelor_leave()
        res.old_children_number = vals.get('children', 0)
        return res

    def write(self, vals):
        if 'marital' in vals:
            for record in self:
                if vals['marital'] == 'single':
                    record.allocate_bachelor_leave()

        if 'children' in vals:
            for record in self:
                old_children_number = record.children
                new_children_number = vals['children']
                if new_children_number > old_children_number:
                    record.allocate_born_leave()
                    record.old_children_number = new_children_number

        return super(EmployeeLeaveAllocation, self).write(vals)

    def allocate_born_leave(self):
        leave_allocation = self.create_leave_allocation(self, 2, 9, 'Allocation de naissance')
        _logger.info(f"Born Allocation Days allocated for {self.name} with ID: {leave_allocation.id}")

    def allocate_bachelor_leave(self):
        leave_allocation = self.create_leave_allocation(self, 2, 8, 'Allocation de Mariage')
        _logger.info(f"Wedding Allocations Days allocated for {self.name} with ID: {leave_allocation.id}")

class ModuleNameInit(models.Model):
    _name = 'module.name.init'
    
    @api.model
    def _create_cron_jobs(self):
        existing_cron = self.env['ir.cron'].search([('name', '=', 'Process Leave Allocations By Month')])
        if not existing_cron:
            self.env['ir.cron'].create({
                'name': 'Process Leave Allocations By Month',
                'interval_type': 'months',
                'interval_number': 1,
                'nextcall': fields.Datetime.now().replace(day=15, hour=0, minute=0, second=0, microsecond=0),
                'model_id': self.env['ir.model'].search([('model', '=', 'hr.employee')]).id,
                'code': 'model.allocate_monthly_leave()',
                'numbercall': -1,
                'user_id': self.env.user.id,
                'priority': 5,
            })

        existing_cron = self.env['ir.cron'].search([('name', '=', 'Process Remote Day By Month')])
        if not existing_cron:
            self.env['ir.cron'].create({
                'name': 'Process Remote Day By Month',
                'interval_type': 'months',
                'interval_number': 1,
                'nextcall': fields.Datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                'model_id': self.env['ir.model'].search([('model', '=', 'hr.employee')]).id,
                'code': 'model.allocate_monthly_remote_day()',
                'numbercall': -1,
                'user_id': self.env.user.id,
                'priority': 5,
            })

    @api.model
    def init(self):
        self._create_cron_jobs()