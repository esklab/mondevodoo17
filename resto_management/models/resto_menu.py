from odoo import models, fields

class RestoMenu(models.Model):
    _name = 'resto.menu'
    _description = 'Menu du Restaurant'

    name = fields.Char(string='Nom du Plat', required=True)
    product_id = fields.Many2one('product.product', string='Produit associé', required=True)
    category = fields.Selection([
        ('starter', 'Entrée'),
        ('main', 'Plat Principal'),
        ('dessert', 'Dessert'),
        ('drink', 'Boisson')
    ], string='Catégorie', required=True)
    description = fields.Text(string='Description')

    price = fields.Float(string='Prix', related='product_id.lst_price', store=True)
