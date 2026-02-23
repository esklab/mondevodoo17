from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    taxe_port = fields.Monetary('Taxe de port', default=0.0, help="Taxe de port")
    ristourne_communale = fields.Monetary('Ristourne communale', default=0.0, help="Taxe de port")
    category_acconage_id = fields.Many2one('dock.category', 'Catégorie acconage', required=True)
    is_transport = fields.Boolean('Est un transport', default=False)
    zone_price_ids = fields.One2many("dock.transport.zone.product_price", "product_id", "Zone pricing")