from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    universe_ids = fields.Many2many('order.universe', string='Univers liés',
                                    help="Univers associés à cette catégorie de produit.")