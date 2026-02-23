from odoo import models, fields, api

class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.model_create_multi
    def create(self, vals_list):
        registrations = super().create(vals_list)
        for reg in registrations:
            if not reg.partner_id and reg.email:
                # Recherche d'un partenaire existant avec le même email
                partner = self.env['res.partner'].search([
                    ('email', '=', reg.email)
                ], limit=1)
                # Création uniquement si aucun partenaire n'existe
                if not partner:
                    partner = self.env['res.partner'].create({
                        'name': reg.name,
                        'email': reg.email,
                        'phone': reg.phone,
                    })
                # Lie le partenaire (existant ou nouveau) à l'inscription
                reg.partner_id = partner
        return registrations