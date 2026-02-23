import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    x_studio_pourcentage_patient = fields.Float(string="Pourcentage du Patient", default=0.0)
    x_studio_total_assurance = fields.Float(string="Total de l'Assurance", compute='_compute_totals', store=True)
    x_studio_total_patient = fields.Float(string="Total du Patient", compute='_compute_totals', store=True)

    @api.depends('line_ids.x_studio_montant_assurance', 'line_ids.x_studio_montant_patient')
    def _compute_totals(self):
        for move in self:
            total_assurance = sum(line.x_studio_montant_assurance for line in move.line_ids)
            total_patient = sum(line.x_studio_montant_patient for line in move.line_ids)
            move.x_studio_total_assurance = total_assurance
            move.x_studio_total_patient = total_patient


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    x_studio_montant_assurance = fields.Float(string="Montant de l'Assurance", compute='_compute_amounts', store=True)
    x_studio_montant_patient = fields.Float(string="Montant du Patient", compute='_compute_amounts', store=True)
    price_subtotal = fields.Float(string="Sous-total", compute='_compute_amounts', store=True)

    @api.depends('move_id.x_studio_pourcentage_patient', 'price_unit', 'quantity')
    def _compute_amounts(self):
        for line in self:
            try:
                _logger.debug("Calcul des montants pour la ligne %s", line.id)

                # Récupérer le pourcentage du patient depuis account.move
                pourcentage_patient = line.move_id.x_studio_pourcentage_patient
                insurance_percentage = 100 - pourcentage_patient

                line.x_studio_montant_assurance = (insurance_percentage / 100.0) * line.price_unit
                line.x_studio_montant_patient = (pourcentage_patient / 100.0) * line.price_unit
                line.price_subtotal = line.price_unit * line.quantity

                _logger.debug("Montants calculés: assurance=%s, patient=%s, subtotal=%s",
                              line.x_studio_montant_assurance,
                              line.x_studio_montant_patient,
                              line.price_subtotal)

            except Exception as e:
                _logger.error("Erreur lors du calcul des montants pour la ligne %s: %s", line.id, e)
                raise e