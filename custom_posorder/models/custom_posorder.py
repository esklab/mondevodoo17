import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def action_pos_order_paid(self):
        res = super().action_pos_order_paid()

        # Chercher la méthode de paiement "Compte Client" dynamiquement une seule fois
        account_payment_method = self.env['pos.payment.method'].search([
            '|',
            ('name', 'ilike', 'Compte Client'),
            ('name', 'ilike', 'Customer Account')
        ], limit=1)

        if not account_payment_method:
            _logger.warning("Méthode de paiement 'Compte Client' ou 'Customer Account' non trouvée.")
            return res  # Sortir proprement si non trouvée

        for order in self:
            try:
                _logger.info(f"Commande {order.name} marquée comme payée.")
                food_lines = order.lines.filtered(lambda l: l.product_id.x_studio_is_food)
                first_payment = order.payment_ids[:1]
                if first_payment:
                    first_payment = first_payment[0]
                    _logger.debug(f"Premier paiement : Méthode {first_payment.payment_method_id.name}, Montant {first_payment.amount} €")

                    if first_payment.payment_method_id.id == account_payment_method.id and food_lines:
                        reservation = self.env['room.booking'].search([
                            ('partner_id', '=', order.partner_id.id),
                            ('state', '=', 'check_in')
                        ], limit=1)

                        if reservation:
                            for line in food_lines:
                                self.env['food.booking.line'].create({
                                    'booking_id': reservation.id,
                                    'food_id': line.product_id.id,
                                    'uom_qty': line.qty,
                                })
                            _logger.info(f"Lignes alimentaires ajoutées à la réservation {reservation.id} pour {order.partner_id.name}")
                        else:
                            _logger.warning(f"Aucune réservation en check-in pour {order.partner_id.name}")
                            raise UserError(
                                f"Aucune réservation en cours (check-in) trouvée pour le client {order.partner_id.name}. "
                                "Veuillez essayer une autre méthode de paiement."
                            )
                else:
                    _logger.debug(f"Aucun paiement trouvé pour la commande {order.name}")
            except Exception as e:
                _logger.exception(f"Erreur dans le traitement de la commande {order.name} : {str(e)}")
        return res
