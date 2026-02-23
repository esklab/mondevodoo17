# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime

class HmsPatient(models.Model):
    _inherit = "hms.patient"

    autorised = fields.Boolean(string='Autorisation medicales de sortie')

class AcsHospitalisation(models.Model):
    _inherit = "acs.hospitalization"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('reserved', 'Reserved'),
        ('hosp','Hospitalized'), 
        ('discharged', 'Discharged'),
        ('autorised', 'Autorisation medicales de sortie'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),], string='Status', default='draft', tracking=True)

    def action_autorise(self):
        for rec in self:
            rec.bed_id.sudo().write({'state': 'free'})
            rec.state = 'autorised'
            rec.discharge_date = datetime.now()
            for history in rec.accommodation_history_ids:
                if rec.bed_id == history.bed_id:
                    history.sudo().end_date = datetime.now()
            rec.patient_id.write({'autorised': True})
