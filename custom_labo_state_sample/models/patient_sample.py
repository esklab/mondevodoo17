from odoo import models, fields, api, _
from odoo.exceptions import UserError 

class PatientLabSample(models.Model):
    _inherit = "acs.patient.laboratory.sample"

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
                raise UserError(_("Record can be delete only in new state."))
        return super(PatientLabSample, self).unlink()

    def action_transfer(self):
        """Action to mark the sample as transferred."""
        self.state = 'transfer'

    def action_recept(self):
        """Action to mark the sample as received at the laboratory."""
        self.state = 'recept'

    def action_treated(self):
        """Action to mark the sample as treated."""
        self.state = 'treated'

    # Update existing methods if needed
    def action_collect(self):
        """Action to mark the sample as collected."""
        self.state = 'collect'

    def action_examine(self):
        """Action to mark the sample as pretreated."""
        self.state = 'examine'

    def action_cancel(self):
        """Action to cancel the sample."""
        self.state = 'cancel'

    def action_reset_to_new(self):
        """Action to reset the sample to 'new' state."""
        self.state = 'new'


class PatientLabTest(models.Model):
    _inherit = "patient.laboratory.test"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validation_technique', 'Validation Technique'),
        ('validation_biologique', 'Validation Biologique'),
        ('done', 'Fait'),
        ('cancel', 'Annulé'),
    ], string='Status', readonly=True, default='draft', tracking=True)

    def action_validation_technique(self):
        """
        Passe de l'état 'draft' à 'validation_technique'.
        """
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("La validation technique ne peut être effectuée qu'à partir de l'état 'Brouillon'."))
            rec.state = 'validation_technique'

    def action_validation_biologique(self):
        """
        Passe de l'état 'validation_technique' à 'validation_biologique'.
        """
        for rec in self:
            if rec.state != 'validation_technique':
                raise UserError(_("La validation biologique ne peut être effectuée qu'à partir de l'état 'Validation Technique'."))
            rec.state = 'validation_biologique'

    def action_done(self):
        """
        Passe de l'état 'validation_biologique' à 'done'.
        """
        for rec in self:
            if rec.state != 'validation_biologique':
                raise UserError(_("L'état 'Terminé' ne peut être atteint qu'à partir de 'Validation Biologique'."))
            rec.consume_lab_material()
            rec.state = 'done'

    def action_cancel(self):
        """
        Permet d'annuler à tout moment.
        """
        for rec in self:
            rec.state = 'cancel'

    def action_draft(self):
        """
        Réinitialise l'état à 'draft'.
        """
        for rec in self:
            if rec.state == 'done':
                raise UserError(_("Vous ne pouvez pas revenir à l'état 'Brouillon' depuis l'état 'Terminé'."))
            rec.state = 'draft'


class LaboratoryRequest(models.Model):
    _inherit = 'acs.laboratory.request'

    def prepare_sample_data(self, line, patient):
        return {
            'sample_type_id': line.test_id.sample_type_id.id if line.test_id.sample_type_id else False,
            'request_id': line.request_id.id if line.request_id else False,
            'user_id': self.env.user.id,
            'patient_id': patient.id,
            'company_id': line.request_id.sudo().company_id.id if line.request_id else False,
            'test_ids': [(4, line.test_id.id)] if line.test_id else [],
        }

    def create_sample(self):
        Sample = self.env['acs.patient.laboratory.sample']
        patients = self.mapped('patient_id') + self.mapped('group_patient_ids')

        for line in self.line_ids:
            if line.test_id.sample_type_id:
                # Vérifier si un échantillon existe déjà
                sample_exist = Sample.search([
                    ('request_id', '=', line.request_id.id),
                    ('sample_type_id', '=', line.test_id.sample_type_id.id)
                ])

                if not sample_exist:
                    # Créer un nouvel échantillon pour chaque patient
                    for patient in patients:
                        lab_sample_data = self.prepare_sample_data(line, patient)
                        Sample.create(lab_sample_data)
                elif not line.test_id.acs_use_other_test_sample:
                    # Si un échantillon existe mais ne peut pas être réutilisé
                    for patient in patients:
                        lab_sample_data = self.prepare_sample_data(line, patient)
                        Sample.create(lab_sample_data)
                else:
                    # Ajouter les tests au sample existant
                    sample_exist.test_ids = [(4, line.test_id.id)]
