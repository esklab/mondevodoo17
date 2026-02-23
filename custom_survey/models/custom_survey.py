# models/custom_survey.py
from odoo import models, fields
from datetime import datetime

class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    agence_id = fields.Many2one('pos.config',string='Agence')

    user_id = fields.Many2one(
        'res.users',
        string="Utilisateur",
        default=lambda self: self.env.user,
        readonly=True,
        ondelete='restrict'
    )

    company_id = fields.Many2one(
        'res.company',
        string="Société",
        default=lambda self: self.env.company,
        readonly=True,
        ondelete='restrict'
    )

    # signature_verificateur = fields.Binary(string="Signature du verificateur")
    # signature_approbateur = fields.Binary(string="Signature du approbateur")
    # signature_redacteur = fields.Binary(string="Signature de l'Opérateur")

    # signature_verificateur_added = fields.Boolean(string="Signature verificateur ajoutée", default=False, readonly=True)
    # signature_approbateur_added = fields.Boolean(string="Signature approbateur ajoutée", default=False, readonly=True)
    # signature_redacteur_added = fields.Boolean(string="Signature Opérateur ajoutée", default=False, readonly=True)

    # date_signature_verificateur = fields.Datetime(string="Date signature verificateur", readonly=True)
    # date_signature_approbateur = fields.Datetime(string="Date signature approbateur", readonly=True)
    # date_signature_redacteur = fields.Datetime(string="Date signature Opérateur", readonly=True)


    # def action_add_verificateur_signature(self):
    #     for rec in self:
    #         if not rec.signature_verificateur_added:
    #             rec.signature_verificateur = self.env.user.sign_signature
    #             rec.signature_verificateur_added = True
    #             rec.date_signature_verificateur = datetime.now()

    # def action_add_approbateur_signature(self):
    #     for rec in self:
    #         if not rec.signature_approbateur_added:
    #             rec.signature_approbateur = self.env.user.sign_signature
    #             rec.signature_approbateur_added = True
    #             rec.date_signature_approbateur = datetime.now()

    # def action_add_redacteur_signature(self):
    #     for rec in self:
    #         if not rec.signature_redacteur_added:
    #             rec.signature_redacteur = self.env.user.sign_signature
    #             rec.signature_redacteur_added = True
    #             rec.date_signature_redacteur = datetime.now()
