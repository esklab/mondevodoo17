from odoo import models, fields, api
from odoo.exceptions import UserError


class NeedExpress(models.Model):
    _name = 'need.express'
    _description = 'need.express'

    date = fields.Date(string='Date')
    product_id = fields.Many2one('product.product', string='Designation')
    quantity = fields.Integer(string='Quantité')
    applicant = fields.Many2one('hr.employee',string='Nom du demandeur',default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    applicant_sign = fields.Binary(string="Signature du demandeur")
    storekeeper_sign = fields.Binary(string="Signature du magasinier")

    @api.model
    def create_purchase_order_from_lines(self, lines):
        order_lines = []
        for ligne in lines:
            product = ligne.product_id
            if not product or not product.exists():
                continue
            order_lines.append((0, 0, {
                'product_id': product.id,
                'name': product.name,
                'product_qty': ligne.quantity,
                'price_unit': product.list_price,
                'product_uom': product.uom_id.id,
            }))

        if not order_lines:
            raise UserError("Aucune ligne valide trouvée.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Bon de commande',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_order_line': order_lines,
            }
        }
