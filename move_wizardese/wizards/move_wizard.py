from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError, UserError


class AccountMoveInsuranceWizard(models.TransientModel):
    _name = 'account.move.insurance.wizard'
    _description = 'Wizard pour le rapport annuel d\'hospitalisation'

    insurance_ids = fields.Many2many('hms.insurance.company', string="Assurances")
    societe_ids = fields.Many2many('res.partner', string="Societes", domain=[('is_company', '=', True)])
    date_from = fields.Date(string="Date de debut")
    date_to = fields.Date(string="Date de fin", default=fields.Date.today)
    move_ids = fields.Many2many('account.move', string="Factures")

    def get_patient_invoices(self):
        domain = [('state', '=', 'posted')]

        if self.insurance_ids:
            domain.append(('x_studio_assurance', 'in', self.insurance_ids.ids))

        # Filtre par sociétés (via patients)
        if self.societe_ids:
            # 1. Trouver les patients liés aux sociétés sélectionnées
            patient_ids = self.env['hms.patient'].search([
                ('x_studio_socit', 'in', self.societe_ids.ids)
            ]).ids
        
            if not patient_ids:
                raise UserError("Aucun patient trouvé pour les sociétés sélectionnées")
        
            # 2. Filtrer les factures de ces patients
            domain.append(('patient_id', 'in', patient_ids))

        if self.date_from:
            domain.append(('invoice_date', '>=', self.date_from))

        if self.date_to:
            domain.append(('invoice_date', '<=', self.date_to))

        return self.env['account.move'].search(domain)

    def action_generate_report(self):
        invoices = self.get_patient_invoices()
        if not invoices:
            raise UserError("Aucune facture trouvée avec les critères sélectionnés.")

        self.move_ids = [(6, 0, invoices.ids)]
        total_amount = sum(invoices.mapped('amount_total'))

        return self.env.ref('move_wizardese.report_account_move_insurance_wizard').report_action(self)
