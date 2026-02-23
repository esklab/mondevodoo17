# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import uuid
import logging
_logger = logging.getLogger(__name__)

class PatientLabTestInherited(models.Model):
    _inherit = "patient.laboratory.test"

    criterea_ids=False

    validation_technique_date = fields.Datetime("Date de validation technique", readonly=True)
    validation_technique_user = fields.Many2one('res.users', "Validé techniquement par", readonly=True)
    validation_biologique_date = fields.Datetime("Date de validation biologique", readonly=True)
    validation_biologique_user = fields.Many2one('res.users', "Validé biologiquement par", readonly=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('validation_technique', 'Validation Technique'),
        ('validation_biologique', 'Validation Biologique'),
        ('done', 'Terminé'),
        ('cancel', 'Annulé'),
    ], string='Status', readonly=True, default='draft', tracking=True)


    def action_done(self):
        for sample_id in self.sample_ids:
            if sample_id.state not in ['treated']:
                raise UserError(_("L'echantillon du patient n'a pas encore été traité."))
        self.consume_lab_material()
        self.state = 'done'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('patient.laboratory.test')
        res = super().create(vals_list)
        for record in res:
            record.unique_code = uuid.uuid4()
            record._subscribe_physician()
        return res

    def write(self, values):
        _logger.info("Entrée dans la méthode write héritée")
        
        for sample_id in self.sample_ids:
            _logger.info(f"Sample ID: {sample_id.id}, State: {sample_id.state}")
            if sample_id.state not in ['treated']:
                raise UserError(_("Les échantillons doivent être traités avant d'effectuer cette action."))
        
        _logger.info("Condition traitée correctement. Appel de la méthode parent.")
        return super(PatientLabTestInherited, self).write(values)

    @api.onchange('test_id')
    def on_change_test(self):
        print('Function deleted')

    def action_validation_technique(self):
        """Valider techniquement et passer à 'Validation Biologique'."""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("La validation technique ne peut être effectuée qu'à partir de l'état 'Brouillon'."))
            rec.validation_technique_date = fields.Datetime.now()
            rec.validation_technique_user = self.env.user
            rec.state = 'validation_biologique'

    def action_validation_biologique(self):
        """Valider biologiquement et terminer le processus."""
        for rec in self:
            if rec.state != 'validation_biologique':
                raise UserError(_("La validation biologique ne peut être effectuée qu'à partir de l'état 'Validation Technique'."))
            rec.validation_biologique_date = fields.Datetime.now()
            rec.validation_biologique_user = self.env.user
            rec.consume_lab_material()
            rec.state = 'done'

    def action_cancel(self):
        """Annuler l'analyse."""
        for rec in self:
            rec.state = 'cancel'

    def action_draft(self):
        """Réinitialiser à l'état 'Brouillon'."""
        for rec in self:
            if rec.state == 'done':
                raise UserError(_("Vous ne pouvez pas revenir à l'état 'Brouillon' depuis l'état 'Terminé'."))
            rec.state = 'draft'


# class ResultatLab(models.Model):
#     _inherit = 'x_resultat_lab'

#     # Champs existants
#     x_studio_resultat_st = fields.Float(string="Résultat ST")
#     x_studio_facteur_de_conversion_1 = fields.Float(string="Facteur de Conversion")
#     x_studio_resultat_si = fields.Float(string="Résultat SI", readonly=True)
#     x_studio_sexe_1 = fields.Selection([
#         ('male', 'Homme'),
#         ('female', 'Femme')
#     ], string="Sexe")
#     x_studio_ref_homme_st = fields.Char(string="Référence Homme")
#     x_studio_ref_femme_st = fields.Char(string="Référence Femme")
#     x_studio_hb = fields.Char(string="Résultat HB", readonly=True)

#     @api.onchange('x_studio_resultat_st', 'x_studio_facteur_de_conversion_1')
#     def _onchange_resultat_st(self):
#         """Calculer x_studio_resultat_si lors du changement de x_studio_resultat_st ou du facteur de conversion."""
#         if self.x_studio_resultat_st and self.x_studio_facteur_de_conversion_1 is not None:
#             if self.x_studio_facteur_de_conversion_1 != 0:
#                 self.x_studio_resultat_si = self.x_studio_resultat_st * self.x_studio_facteur_de_conversion_1
#             else:
#                 _logger.info(f"Facteur de conversion est 0 pour la ligne {self.id}")
#         else:
#             _logger.warning(f"Champs nécessaires manquants pour la ligne {self.id}")

#     @api.onchange('x_studio_sexe_1', 'x_studio_ref_homme_st', 'x_studio_ref_femme_st', 'x_studio_resultat_st')
#     def _onchange_resultat_hb(self):
#         """Calculer x_studio_hb en fonction des champs changés."""
#         reference = None
#         if self.x_studio_sexe_1 == 'male':
#             reference = self.x_studio_ref_homme_st
#         elif self.x_studio_sexe_1 == 'female':
#             reference = self.x_studio_ref_femme_st

#         res_hb = ''
#         if reference and self.x_studio_resultat_st != 0.0:
#             try:
#                 # Remplacer la virgule par un point et séparer les limites
#                 limites = reference.replace(',', '.').split('-')

#                 # Vérification si les limites sont valides (deux valeurs)
#                 if len(limites) == 2:
#                     ref_min = float(limites[0])
#                     ref_max = float(limites[1])

#                     # Calcul du résultat en fonction du résultat ST
#                     if ref_min <= self.x_studio_resultat_st <= ref_max:
#                         res_hb = 'N'  # Le résultat est dans les limites
#                     elif self.x_studio_resultat_st < ref_min:
#                         res_hb = 'B'  # Le résultat est en dessous des limites
#                     else:
#                         res_hb = 'H'  # Le résultat est au-dessus des limites
#                 else:
#                     res_hb = ''  # Si les limites ne sont pas valides
#             except ValueError as e:
#                 # Loguer une erreur si la conversion échoue
#                 _logger.error(f"Erreur de conversion pour la référence '{reference}': {str(e)}")
#                 res_hb = ''  # En cas d'erreur, on laisse le champ vide

#         # Mettre à jour le champ avec le résultat
#         self.x_studio_hb = res_hb
