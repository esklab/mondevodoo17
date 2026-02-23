from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PatientLabSample(models.Model):
    _inherit = "acs.patient.laboratory.sample"

    date_collect = fields.Datetime("Date de prélèvement", readonly=True)
    user_collect = fields.Many2one('res.users', "Prélevé par", readonly=True)
    date_recept = fields.Datetime("Date de réception", readonly=True)
    user_recept = fields.Many2one('res.users', "Réceptionné par", readonly=True)
    date_examine = fields.Datetime("Date d'examen", readonly=True)
    user_examine = fields.Many2one('res.users', "Examiné par", readonly=True)
    date_treated = fields.Datetime("Date du résultat", readonly=True)
    user_treated = fields.Many2one('res.users', "Traité par", readonly=True)
    date_transfer = fields.Datetime("Date de transport", readonly=True)  # Ajout de la date de transport
    user_transfer = fields.Many2one('res.users', "Transporté par", readonly=True)  # Ajout de l'utilisateur responsable du transport

    state = fields.Selection([
        ('new', 'Nouveau'),
        ('collect', 'Prélevé'),
        ('transfer', 'Transporté'),
        ('recept', 'Réceptionné au laboratoire'),
        ('examine', 'Prétraité'),
        ('treated', 'Traité'),
        ('cancel', 'Annulé'),
    ], string='Status', readonly=True, default='new')

    def unlink(self):
        for rec in self:
            if rec.state not in ['new']:
                raise UserError(_("Seuls les enregistrements à l'état 'Nouveau' peuvent être supprimés."))
        return super(PatientLabSample, self).unlink()

    def action_collect(self):
        """Marquer l'échantillon comme prélevé."""
        self.state = 'collect'
        self.date_collect = fields.Datetime.now()
        self.user_collect = self.env.user

    def action_transfer(self):
        """Marquer l'échantillon comme transporté."""
        self.state = 'transfer'
        self.date_transfer = fields.Datetime.now()  # Enregistrement de la date de transport
        self.user_transfer = self.env.user  # Enregistrement de l'utilisateur responsable du transport

    def action_recept(self):
        """Marquer l'échantillon comme réceptionné."""
        self.state = 'recept'
        self.date_recept = fields.Datetime.now()
        self.user_recept = self.env.user

    def action_examine(self):
        for rec in self:
            # Vérifier si la requête existe
            if not rec.request_id:
                raise UserError("L'échantillon n'est lié à aucune requête de laboratoire.")
        
            # Parcourir les lignes de la requête pour vérifier le champ x_studio_ne_ncessite_pas_de_prtraitement
            if rec.request_id.line_ids.filtered(lambda line: line.test_id.x_studio_ne_ncessite_pas_de_prtraitement):
                # Si un test ne nécessite pas de prétraitement
                rec.state = 'treated'
                rec.date_treated = fields.Datetime.now()
                rec.user_treated = self.env.user
            else:
                # Si tous les tests nécessitent un prétraitement
                rec.state = 'examine'
                rec.date_examine = fields.Datetime.now()
                rec.user_examine = self.env.user

    def action_treated(self):
        """Marquer l'échantillon comme traité."""
        if self.state != 'treated':
            # Marquer l'échantillon comme traité
            self.write({
                'state': 'treated',
                'date_treated': fields.Datetime.now(),
                'user_treated': self.env.user.id,
            })
        # Vérifier si tous les échantillons de la requête sont à l'état 'treated'
        if self.request_id:
            all_samples_treated = all(sample.state == 'treated' for sample in self.request_id.sample_ids)
            if all_samples_treated:
                self.request_id.button_in_progress()

    def action_cancel(self):
        """Annuler l'échantillon."""
        self.state = 'cancel'

    def action_reset_to_new(self):
        """Réinitialiser l'état à 'Nouveau'."""
        self.state = 'new'