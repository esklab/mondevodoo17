from odoo import models, fields, api, _

class EventRegistration(models.Model):
    _inherit = 'event.registration'
    
    state = fields.Selection(
        selection_add=[
            ('preinscript', 'Préinscrit'),
            ('open', 'Inscrit'),
            ('declin', 'Declin'),
            ('done', 'Present')
        ],
        default='preinscript'  # État par défaut après création
    )
    
    def action_confirm_registration(self):
        """Valide l'inscription et envoie le ticket"""
        for registration in self:
            # Change l'état à 'Inscrit'
            registration.write({'state': 'open'})
            
            # Envoie l'email de confirmation avec le ticket
            registration._send_ticket()
            
        return True
    
    def _send_ticket(self):
        """Envoie le ticket par email"""
        template = self.env.ref('event.event_registration_mail_template_barcode')
        if template:
            template.send_mail(self.id, force_send=True)
    
    def action_decline(self):
        """Décline l'inscription et SUPPRIME l'enregistrement"""
        self.unlink()  # Supprime l'inscription
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',  # Recharge la vue pour actualiser
        }
        
    @api.model_create_multi
    def create(self, vals_list):
        """Surcharge de la création pour définir l'état initial"""
        registrations = super().create(vals_list)
        # Pas besoin de set state ici car le default est déjà défini
        return registrations