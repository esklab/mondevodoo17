from odoo import models, fields, api

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    amount = fields.Monetary(default=0.0)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self._context.get('active_id')
        if active_id:
            move = self.env['account.move'].browse(active_id)
            if move:
                res['amount'] = move.x_studio_total_montant_paye_patient
        return res

    @api.onchange('journal_id')
    def _onchange_journal_id_custom(self):
        active_id = self._context.get('active_id')
        if active_id:
            move = self.env['account.move'].browse(active_id)
            if move:
                self.amount = move.x_studio_total_montant_paye_patient
