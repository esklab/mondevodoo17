from odoo import models

class PosOrderReport(models.Model):
    _inherit = 'report.pos.order'

    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False):
        res = super().get_sale_details(date_start, date_stop, config_ids, session_ids)
        
        # Ajouter les données clients
        domain = [('state', 'in', ['paid', 'invoiced', 'done'])]
        if session_ids:
            domain = [('session_id', 'in', session_ids)]
        else:
            domain = [
                ('date_order', '>=', date_start),
                ('date_order', '<=', date_stop)
            ]
            if config_ids:
                domain.append(('config_id', 'in', config_ids))
        
        orders = self.env['pos.order'].search(domain)
        
        customer_data = []
        for order in orders:
            if order.partner_id:
                customer_data.append({
                    'order_name': order.name,
                    'customer_name': order.partner_id.name,
                    'customer_phone': order.partner_id.phone or 'N/A',
                    'customer_email': order.partner_id.email or 'N/A',
                    'date_order': order.date_order,
                    'amount_total': order.amount_total
                })
        
        res['customer_data'] = customer_data
        return res