from odoo import models, fields, api
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    assurance_id = fields.Many2one('hms.insurance.company','string',)
    pourcentage_patient = fields.Float(string="Pourcentage du Patient", default=1.0)
    total_assurance = fields.Monetary(string="Total de l'Assurance", compute='_compute_totals', store=True, currency_field='currency_id')
    total_patient = fields.Monetary(string="Total du Patient", compute='_compute_totals', store=True, currency_field='currency_id')

    @api.constrains('pourcentage_patient')
    def _check_pourcentage_patient(self):
        for order in self:
            if not (0 <= order.pourcentage_patient <= 100):
                raise ValidationError("Le pourcentage du patient doit être compris entre 0 et 100.")

    @api.depends('order_line.montant_assurance', 'order_line.montant_patient')
    def _compute_totals(self):
        for order in self:
            total_assurance = sum(line.montant_assurance * line.product_uom_qty for line in order.order_line)
            total_patient = sum(line.montant_patient * line.product_uom_qty for line in order.order_line)
            order.total_assurance = total_assurance
            order.total_patient = total_patient


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    montant_assurance = fields.Monetary(string="Montant de l'Assurance", compute='_compute_amounts', store=True, currency_field='currency_id')
    montant_patient = fields.Monetary(string="Montant du Patient", compute='_compute_amounts', store=True, currency_field='currency_id')
    price_subtotal = fields.Monetary(string="Sous-total", compute='_compute_amounts', store=True, currency_field='currency_id')

    @api.depends('order_id.pourcentage_patient', 'price_unit', 'product_uom_qty')
    def _compute_amounts(self):
        for line in self:
            try:
                _logger.debug("Calcul des montants pour la ligne %s", line.id)

                # Récupérer le pourcentage du patient depuis sale.order
                pourcentage_patient = line.order_id.pourcentage_patient
                insurance_percentage = 100 - pourcentage_patient

                line.montant_assurance = (insurance_percentage / 100.0) * line.price_unit
                line.montant_patient = (pourcentage_patient / 100.0) * line.price_unit
                line.price_subtotal = line.price_unit * line.product_uom_qty

                _logger.debug("Montants calculés: assurance=%s, patient=%s, subtotal=%s",
                              line.montant_assurance,
                              line.montant_patient,
                              line.price_subtotal)

            except Exception as e:
                _logger.error("Erreur lors du calcul des montants pour la ligne %s: %s", line.id, e)
                raise e