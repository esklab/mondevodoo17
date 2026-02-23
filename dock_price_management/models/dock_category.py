# models/dock_category.py

from odoo import models, fields, api, _


class DockCategory(models.Model):
    _name = 'dock.category'
    _description = 'Catégories Acconage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(string='Nom Catégorie', required=True, tracking=True)
    code = fields.Char(
        string='Code',
        tracking=True,
    )
    type = fields.Selection([('import', 'Import'), ('export', 'Export')], default=False,
                            required=True)

    sequence = fields.Integer(
        string='Séquence',
        default=10,
    )

    active = fields.Boolean(
        string='Actif',
        default=True,
        tracking=True,
    )

    description = fields.Text(
        string='Description',
        tracking=True,
    )
    order_universe_id = fields.Many2one('order.universe', string="Univers de Commande",
                                        help="Sélectionnez l'univers associé à cette commande.")

    product_ids = fields.Many2many(
        'product.product',
        string='Articles associés',
        tracking=True,
    )

    dock_price_ids = fields.One2many(
        'dock.price',
        'dock_category_id',
        string='Prix d\'acconage',
    )

    _sql_constraints = [
        ('unique_code',
         'UNIQUE(code)',
         'Le code doit être unique !')
    ]