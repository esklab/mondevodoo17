import logging
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    waste_material = fields.Float(string="Matériau perdu estimé", compute="_compute_waste")
    suggested_products = fields.Many2many('product.product', string="Produits suggérés")

    @api.depends('bom_line_ids')
    def _compute_waste(self):
        for bom in self:
            total_loss = 0
            suggested = []

            # Récupérer les dimensions du bloc principal (matière première)
            bloc = bom.bom_line_ids.filtered(lambda l: l.product_id.type == 'raw')[0]
            bloc_longueur = bloc.product_id.longueur
            bloc_largeur = bloc.product_id.largeur

            # Récupérer les dimensions du produit fabriqué
            produit_longueur = bom.product_tmpl_id.longueur
            produit_largeur = bom.product_tmpl_id.largeur

            # Calcul des chutes après découpe
            reste_longueur = bloc_longueur - produit_longueur
            reste_largeur = bloc_largeur - produit_largeur

            if reste_longueur > 0 and reste_largeur > 0:
                total_loss = reste_longueur * reste_largeur

                # Trouver des accessoires pouvant être fabriqués avec les chutes
                accessoires = self.env['product.product'].search([
                    ('type', '=', 'accessory'),
                    ('longueur', '<=', reste_longueur),
                    ('largeur', '<=', reste_largeur)
                ], limit=5)

                suggested.extend(accessoires.ids)

            bom.waste_material = total_loss
            bom.suggested_products = [(6, 0, suggested)]
