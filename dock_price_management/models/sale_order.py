from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_universe_id = fields.Many2one('order.universe', string="Univers de Commande",
                                        help="Sélectionnez l'univers associé à cette commande.")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def _onchange_product_id_universe(self):
        if self.order_id.order_universe_id and self.product_id:
            allowed_categories = self.order_id.order_universe_id.category_ids
            if self.product_id.categ_id not in allowed_categories:
                self.product_id = False
                return {
                    'warning': {
                        'title': "Produit Invalide",
                        'message': "Ce produit ne fait pas partie de l'univers de commande sélectionné.",
                    }
                }