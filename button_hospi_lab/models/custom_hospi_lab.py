import logging
from odoo import models, fields, api

class AcsLaboratoryRequest(models.Model):
    _inherit = "acs.laboratory.request"

    emergency_id = fields.Many2one('acs.hms.emergency', string="Emergency")

class Emergency(models.Model):
    _inherit = "acs.hms.emergency"

    request_ids = fields.One2many('acs.laboratory.request', 'emergency_id', string='Lab Requests')

    def action_lab_request(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_laboratory.hms_action_lab_test_request")
        action['domain'] = [('id', 'in', self.request_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_emergency_id': self.id}
        action['views'] = [(self.env.ref('acs_laboratory.patient_laboratory_test_request_form').id, 'form')]
        return action
