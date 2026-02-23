from odoo import models

class HmsAppointment(models.Model):
    _inherit = 'hms.appointment'

    def action_print_appointments_by_doctor(self):
        return self.env.ref('custom_report.report_appointments_by_doctor').report_action(self)
