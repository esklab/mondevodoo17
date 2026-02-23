from odoo import models, fields, api
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_id_ids = fields.Many2many('account.payment',string='Payments', compute='_compute_payment_ids')

    @api.depends('line_ids')
    def _compute_payment_ids(self):
        for move in self:
            payments = self.env['account.payment'].search([
                ('move_id', 'in', move.line_ids.mapped('matched_debit_ids.debit_move_id.move_id.id') +
                 move.line_ids.mapped('matched_credit_ids.credit_move_id.move_id.id'))
            ])
            move.payment_id_ids = payments

