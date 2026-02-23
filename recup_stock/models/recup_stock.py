from odoo import models, fields, api

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    qty_available_in_location = fields.Float(
        string='Quantité disponible',
        compute='_compute_qty_available_in_location',
        store=False
    )

    @api.depends('product_id', 'order_id')
    def _compute_qty_available_in_location(self):
        for line in self:
            # location = line.order_id.location_id
            location = line.order_id.x_studio_location
            product = line.product_id
            qty = 0.0
            if product and location:
                stock_quant = self.env['stock.quant'].sudo().search([
                    ('product_id', '=', product.id),
                    ('location_id', '=', location.id)
                ], limit=1)
                qty = stock_quant.quantity if stock_quant else 0.0
            line.qty_available_in_location = qty
