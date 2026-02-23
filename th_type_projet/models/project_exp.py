from odoo import api, fields, models
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class ProjectProject(models.Model):
    _inherit = 'project.project'

    real_end_date = fields.Date('Real End Date', compute='_compute_real_end_date',store=True)

    @api.depends('task_ids.duration')
    def _compute_real_end_date(self):
        for project in self:
            total_duration = sum(task.duration for task in project.task_ids)
            if project.date_start and total_duration:
                try:
                    project.write({'real_end_date': project.date_start + timedelta(days=total_duration)})
                except Exception as e:
                    _logger.error(f"Error computing real_end_date: {e}")

class ProjectTask(models.Model):
    _inherit = 'project.task'
    duration = fields.Integer('Duration (days)', compute='_compute_duration_days')

    @api.depends('date_deadline', 'create_date')
    def _compute_duration_days(self):
        for task in self:
            if task.date_deadline and task.create_date:
                # Convert create_date to datetime.date
                create_date = fields.Datetime.from_string(task.create_date)
                create_date = create_date.date()

                # Calculate duration in days
                duration = (task.date_deadline.date() - create_date).days
                task.duration = duration
            else:
                task.duration = 0


        

