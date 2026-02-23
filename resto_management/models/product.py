from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_resto = fields.Boolean(string='Produit Restaurant', default=False)

    _logger.info("Chargement du modèle ProductTemplate avec is_resto")

class PosOrder(models.Model):
    _inherit = 'pos.order'
