import logging
from odoo import models, fields, api

class Emergency(models.Model):
    _inherit = "acs.radiology.request"

    emergency_id = fields.Many2one('acs.hms.emergency', string="Emergency")

class Emergency(models.Model):
    _inherit = "acs.hms.emergency"

    radiology_request_ids = fields.One2many('acs.radiology.request', 'emergency_id', string='Radiology Requests')

    def action_radiology_request(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_radiology.hms_action_radiology_request")
        action['domain'] = [('id', 'in', self.radiology_request_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_emergency_id': self.id}
        action['views'] = [(self.env.ref('acs_radiology.patient_radiology_test_request_form').id, 'form')]
        return action
