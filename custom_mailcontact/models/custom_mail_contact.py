from odoo import models, api

class MailingContact(models.Model):
    _inherit = 'mailing.contact'

    @api.model_create_multi
    def create(self, vals_list):
        contacts = super().create(vals_list)
        # Créer les partenaires correspondants
        for contact in contacts:
            self.env['res.partner'].create({
                'name': contact.name,
                'email': contact.email,
                'is_mailing_contact': True, 
                'title_id':contact.title_id,
                'company_name':contact.company_name,
                'country_id':contact.country_id
            })
        return contacts