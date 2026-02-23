from odoo import models, fields, api
from num2words import num2words

class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_in_words = fields.Char(string="Montant en lettres", compute="_compute_amount_in_words")

    @api.depends('tax_totals')
    def _compute_amount_in_words(self):
        for record in self:
            if record.tax_totals:
                record.amount_in_words = num2words(record.tax_totals, lang='fr')
            else:
                record.amount_in_words = ""
