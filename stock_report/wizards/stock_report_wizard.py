from odoo import models, fields, api

class StockReportWizard(models.TransientModel):
    _name = 'stock.report.wizard'
    _description = "Stock Report Wizard"

    location_id = fields.Many2one('stock.location', string="Emplacement")
    category_id = fields.Many2one('product.category', string="Catégorie")
    date_start = fields.Date(string="Date de début")
    date_end = fields.Date(string="Date de fin")

    def action_generate_report(self):
        """ Génère le rapport en fonction des critères du wizard """
        data = {
            'location_id': self.location_id.id,
            'category_id': self.category_id.id,
            'date_start': self.date_start,
            'date_end': self.date_end
        }
        return self.env.ref('stock_report.stock_report_action').report_action(self, data=data)
