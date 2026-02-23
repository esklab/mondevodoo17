import logging
from odoo import models, fields, api
from num2words import num2words


_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    x_studio_prix_conventionne = fields.Float(string="Prix conventionné", default=0.0)


class AccountMove(models.Model):
    _inherit = 'account.move'

    patient_id = fields.Many2one('hms.patient', string="Patient")
    x_studio_taux_de_couverture = fields.Float(
        string="Taux de Couverture (%)",
        help="Taux de couverture de l'assurance pour le patient.",
        default=0.0
    )
    x_studio_total_assurance = fields.Float(
        string="Total de l'Assurance", 
        compute='_compute_totals', 
        store=True
    )
    x_studio_total_patient = fields.Float(
        string="Total du Patient", 
        compute='_compute_totals', 
        store=True
    )
    x_studio_total_montant_paye_patient = fields.Float(
        string="Montant Total Payé par le Patient",
        compute="_compute_totals",
        store=True,
        help="Somme de tous les montants payés par le patient sur les lignes de la facture."
    )

    x_studio_montant_a_pay_en_lettre = fields.Char(
        string="Montant en Lettre",
        compute="_compute_montant_en_lettre",
        store=True
    )

    @api.depends('x_studio_total_montant_paye_patient')
    def _compute_montant_en_lettre(self):
        """Convertit le montant total payé par le patient en lettres."""
        for record in self:
            try:
                if record.x_studio_total_montant_paye_patient:
                    record.x_studio_montant_a_pay_en_lettre = num2words(
                        record.x_studio_total_montant_paye_patient, lang='fr'
                    ).capitalize()
                else:
                    record.x_studio_montant_a_pay_en_lettre = ''
            except Exception as e:
                _logger.error("Erreur lors de la conversion du montant en lettres: %s", e)
                record.x_studio_montant_a_pay_en_lettre = "Erreur de conversion"

    @api.model
    def create(self, vals):
        """Ajoute le taux de couverture à la création de la facture."""
        record = super(AccountMove, self).create(vals)
        if 'patient_id' in vals:
            record._apply_patient_coverage()
        return record

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        """Récupère le taux de couverture depuis le patient sélectionné."""
        self._apply_patient_coverage()

    def _apply_patient_coverage(self):
        """Applique le taux de couverture du patient à la facture et à ses lignes."""
        for move in self:
            move.x_studio_taux_de_couverture = move.patient_id.x_studio_taux_de_couverture or 0.0
            # Mise à jour des lignes immédiatement
            for line in move.line_ids:
                line.x_studio_taux_de_couverture = move.x_studio_taux_de_couverture
            move._compute_totals()

    @api.onchange('x_studio_taux_de_couverture')
    def _onchange_x_studio_taux_de_couverture(self):
        """Met à jour le taux de couverture des lignes lorsque le taux de la facture change."""
        for move in self:
            for line in move.line_ids:
                line.x_studio_taux_de_couverture = move.x_studio_taux_de_couverture

    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        """Recalcule les totaux lorsque les lignes sont modifiées."""
        self._compute_totals()

    @api.depends('line_ids.x_studio_montant_assurance', 'line_ids.x_studio_montant_patient', 'line_ids.x_studio_montant_paye_patient')
    def _compute_totals(self):
        """Calcule les totaux de l'assurance, du patient et du montant payé par le patient."""
        for move in self:
            move.x_studio_total_assurance = sum(
                line.x_studio_montant_assurance for line in move.line_ids
            )
            move.x_studio_total_patient = sum(
                line.x_studio_montant_patient for line in move.line_ids
            )
            move.x_studio_total_montant_paye_patient = sum(
                line.x_studio_montant_paye_patient for line in move.line_ids
            )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    x_studio_taux_de_couverture = fields.Float(
        string="Taux de Couverture (%)",
        help="Taux de couverture spécifique pour cette ligne. Par défaut, utilise le taux global défini dans la facture."
    )
    x_studio_montant_assurance = fields.Float(string="Montant de l'Assurance", compute='_compute_amounts', store=True)
    x_studio_montant_patient = fields.Float(string="Montant du Patient", compute='_compute_amounts', store=True)
    x_studio_prix_conventionne = fields.Float(string="Prix Conventionné", default=0.0)
    x_studio_montant_paye_patient = fields.Float(string="Montant Payé par le Patient", compute='_compute_amounts', store=True)
    price_subtotal = fields.Float(string="Sous-total", compute='_compute_amounts', store=True)

    @api.onchange('x_studio_montant_assurance', 'x_studio_montant_patient', 'x_studio_montant_paye_patient')
    def _onchange_line_totals(self):
        """Recalcule les totaux de la facture lorsque les valeurs des lignes changent."""
        if self.move_id:
            self.move_id._compute_totals()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Met à jour x_studio_prix_conventionne en fonction du produit sélectionné."""
        for line in self:
            if line.product_id and not line.x_studio_prix_conventionne:
                line.x_studio_prix_conventionne = line.product_id.product_tmpl_id.x_studio_prix_convenus or line.price_unit
    
            # Récupérer automatiquement le taux de couverture de la facture (move_id) et le mettre à jour sur la ligne
            if line.move_id and line.move_id.x_studio_taux_de_couverture:
                line.x_studio_taux_de_couverture = line.move_id.x_studio_taux_de_couverture

    @api.depends('x_studio_taux_de_couverture', 'move_id.x_studio_taux_de_couverture', 'x_studio_prix_conventionne', 'price_unit', 'quantity')
    def _compute_amounts(self):
        """Calcule les montants pour l'assurance, le patient et le montant payé par le patient."""
        for line in self:
            try:
                _logger.debug("Calcul des montants pour la ligne %s", line.id)

                # Utiliser le taux de couverture spécifique à la ligne ou celui de la facture
                taux_de_couverture = line.x_studio_taux_de_couverture or line.move_id.x_studio_taux_de_couverture or 0.0
                pourcentage_patient = 1 - (taux_de_couverture / 100.0)

                # Utiliser le prix convenu
                prix_conventionne = line.x_studio_prix_conventionne or line.price_unit

                # Calcul des parts
                part_assuree = prix_conventionne * (taux_de_couverture / 100.0)
                part_assurance = prix_conventionne * pourcentage_patient

                # Montant payé par le patient
                montant_paye_patient = part_assurance + (line.price_unit - prix_conventionne)

                # Mise à jour des champs
                line.x_studio_montant_assurance = part_assuree * line.quantity
                line.x_studio_montant_patient = part_assurance * line.quantity
                line.x_studio_montant_paye_patient = montant_paye_patient * line.quantity
                line.price_subtotal = prix_conventionne * line.quantity

                _logger.debug(
                    "Montants calculés: assurance=%s, patient=%s, payé par patient=%s, subtotal=%s",
                    line.x_studio_montant_assurance,
                    line.x_studio_montant_patient,
                    line.x_studio_montant_paye_patient,
                    line.price_subtotal
                )

            except Exception as e:
                _logger.error("Erreur lors du calcul des montants pour la ligne %s: %s", line.id, e)
                raise e
