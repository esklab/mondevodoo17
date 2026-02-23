from odoo import models, api, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def _get_user_job(self):
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee.job_id.name if employee and employee.job_id else None

    def action_post(self):
        for payment in self:
            if payment.payment_type == 'outbound':  # Paiement fournisseur
                job_name = self._get_user_job()
                amount = payment.amount

                if amount <= 50000:
                    if job_name not in ['Directeur Financier et Comptable', 'Chef Comptable']:
                        raise UserError(_("Seuls le DFC ou le Chef Comptable peuvent valider les paiements de 50 000 FCFA ou moins."))
                else :
                    if job_name not in ['Directeur Financier et Comptable', 'PCA', "Directeur de l'Administration des Ressources Humaines et de la Logistique"]:
                        raise UserError(_("Seuls le DFC, le PCA ou la DARHL peuvent valider les paiements superieurs a 50 000 FCFA."))

        return super(AccountPayment, self).action_post()