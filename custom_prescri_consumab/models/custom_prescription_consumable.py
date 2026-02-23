# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HMSConsumableLine(models.Model):
    _inherit = 'hms.consumable.line'
    
    prescription_line_id = fields.Many2one('prescription.line', string='Ligne de prescription')

class PrescriptionOrderLine(models.Model):
    _inherit = 'prescription.line'
    
    consumable_line_id = fields.Many2one('hms.consumable.line', string='Ligne de consommable liee')
    
    _sql_constraints = [
        ('unique_prescription_consumable', 
         'UNIQUE(consumable_line_id)', 
         'Une ligne de prescription ne peut être lier a une seule ligne de consommable')
    ]

class PrescriptionOrder(models.Model):
    _inherit = 'prescription.order'
    
    def action_prescription_confirm(self):
        """Override confirm action to auto-create consumables"""
        res = super().action_prescription_confirm()
        self.sync_prescription_to_consumables()
        return res
    
    def action_sync_to_consumables(self):
        """Manual sync button action"""
        self.sync_prescription_to_consumables()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Les medicaments sont ajoutes aux consommables'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def sync_prescription_to_consumables(self):
        """Main sync method"""
        ConsumableLine = self.env['hms.consumable.line']
        for prescription in self:
            if not prescription.hospitalization_id:
                raise ValidationError(_("Cette ordonnance n'est pas liee a une hospitalisation"))
            
            for line in prescription.prescription_line_ids:
                if not line.consumable_line_id:
                    consumable_line = ConsumableLine.create({
                        'hospitalization_id': prescription.hospitalization_id.id,
                        'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'qty': line.quantity,
                        'prescription_line_id': line.id,
                        'date': fields.Datetime.now(),
                    })
                    line.consumable_line_id = consumable_line.id