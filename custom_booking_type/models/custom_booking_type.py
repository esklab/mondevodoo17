import logging
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

from odoo import models, fields

class AppointmentSlot(models.Model):
    _inherit = "appointment.slot"

    resource_id = fields.Many2one(
        "resource.resource",
        string="Ressource assignée",
        domain="[]",  # Initialement, on ne met pas de domaine ici
        help="Sélectionnez la ressource spécifique pour ce créneau."
    )

    @api.onchange('appointment_type_id')
    def _onchange_appointment_type(self):
        """Met à jour dynamiquement les ressources en fonction du type de rendez-vous"""
        if self.appointment_type_id:
            self.resource_id = False
            return {
                'domain': {
                    'resource_id': [('id', 'in', self.appointment_type_id.resource_ids.ids)]
                }
            }

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    resource_id = fields.Many2one("resource.resource", string="Ressource assignée")

    @api.onchange('start')
    def _onchange_start(self):
        """Met à jour la ressource en fonction du créneau sélectionné"""
        if self.start:
            slot = self.env['appointment.slot'].search([
                ('start_datetime', '<=', self.start),
                ('end_datetime', '>=', self.start)
            ], limit=1)
            self.resource_id = slot.resource_id if slot else False
