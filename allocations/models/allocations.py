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
                'nextcall': fields.Datetime.now().replace(day=28, hour=23, minute=59, second=0, microsecond=0),
                'model_id': self.env['ir.model'].search([('model', '=', 'hr.employee')]).id,
                'code': 'model.allocate_monthly_leave()',
                'numbercall': -1,
                'user_id': self.env.user.id,
                'priority': 5,
            })

    @api.model
    def init(self):
        self._create_cron_jobs()