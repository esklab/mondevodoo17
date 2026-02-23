from odoo import models, fields


class OrderUniverse(models.Model):
    _name = 'order.universe'
    _description = 'Univers de Commande'

    name = fields.Char(string="Univers", required=True)
    code = fields.Char(string="Code", required=True, help="Code court unique pour l'univers (ex : AIR, TER, MAR)")
    category_ids = fields.Many2many('product.category', string='Catégories Liées',
                                    help="Catégories de produits associées à cet univers.")