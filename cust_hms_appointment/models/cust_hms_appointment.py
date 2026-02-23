from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    appointment_id = fields.Many2one(
        'hms.appointment', string='Rendez-vous', readonly=True, ondelete='set null'
    )
    
class HmsAppointment(models.Model):
    _inherit = 'hms.appointment'

    payment_ids = fields.One2many(
        'account.payment', compute='_compute_payment_ids', string='Paiements liés', readonly=True
    )

    @api.depends('invoice_ids.payment_state')
    def _compute_payment_ids(self):
        for rec in self:
            payments = self.env['account.payment'].browse()
            for invoice in rec.invoice_ids:
                # Récupérer les paiements liés à la facture
                payments |= invoice._get_reconciled_payments()
            rec.payment_ids = payments

    def action_view_payments(self):
        self.ensure_one()
        payments = self.payment_ids
        return {
            'name': 'Paiements liés',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', payments.ids)],
            'context': {'create': False},
        }
