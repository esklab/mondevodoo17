from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    has_tva = fields.Boolean(string="A TVA", default=False)
