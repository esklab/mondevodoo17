import logging
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create(self, vals):
        """ Vérifie si un contact existe déjà avec le même email ou téléphone. 
            - Si oui, retourne ce contact sans en créer un nouveau.
            - Sinon, crée un nouveau contact. """
        email = vals.get('email')
        phone = vals.get('phone')

        _logger.info("Tentative de création d'un contact avec Email: %s | Téléphone: %s", email, phone)

        domain = ['|', ('email', '=', email), ('phone', '=', phone)]  # Vérifie si l'un des deux existe

        existing_partner = self.env['res.partner'].search(domain, limit=1)
        if existing_partner:
            _logger.info("Un contact existant a été trouvé : %s (ID: %d), utilisation de ce contact.", existing_partner.name, existing_partner.id)
            return existing_partner  # Retourne le contact existant au lieu d'en créer un nouveau

        new_partner = super(ResPartner, self).create(vals)
        _logger.info("Nouveau contact créé : %s (ID: %d)", new_partner.name, new_partner.id)
        return new_partner