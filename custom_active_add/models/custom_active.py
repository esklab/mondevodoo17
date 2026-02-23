from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_active = fields.Boolean(default=True)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_active = fields.Boolean(default=True)

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_active = fields.Boolean(default=True)