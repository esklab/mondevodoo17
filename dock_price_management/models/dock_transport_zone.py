# models/dock_transport_zone.py

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DockTransportZone(models.Model):
    _name = 'dock.transport.zone'
    _description = 'Zone de Transport'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(
        string='Nom Zone',
        required=True,
        tracking=True,
    )

    code = fields.Char(
        string='Code',
        tracking=True,
    )

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

    distance = fields.Float(
        string='Distance (km)',
        tracking=True,
    )

    base_price = fields.Float(
        string='Prix de Base',
        tracking=True,
        help="Prix de base pour cette zone de transport",
    )

    # city_ids = fields.Many2many(
    #     'res.city',
    #     string='Villes',
    #     tracking=True,
    # )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='État', default='draft', tracking=True)

    _sql_constraints = [
        ('unique_code',
         'UNIQUE(code)',
         'Le code de la zone de transport doit être unique !')
    ]

    @api.constrains('base_price')
    def _check_base_price(self):
        for record in self:
            if record.base_price < 0:
                raise ValidationError(_("Le prix de base ne peut pas être négatif."))

    def action_activate(self):
        self.write({'state': 'active'})

    def action_deactivate(self):
        self.write({'state': 'inactive'})


class DockTransportZoneProcutPrice(models.Model):
    _name = 'dock.transport.zone.product_price'
    _description = 'Prix du transport par Zone de Transport'

    zone_id = fields.Many2one('dock.transport.zone',string='Zone de Transport',
        required=True, tracking=True)
    price = fields.Float("Prix", required=True)
    product_id = fields.Many2one("product.template", "Produit", required=False)