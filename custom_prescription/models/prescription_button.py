from odoo import models, fields, api
from odoo.exceptions import UserError

class PrescriptionOrder(models.Model):
    _inherit = 'prescription.order'

    submit_state = fields.Selection([
        ('draft', 'Pas encore soumis'),
        ('submitted', 'Soumis à la pharmacie')
    ], default='draft', string="État", tracking=True)

    x_studio_livraison_id = fields.Many2one('stock.picking', string="Livraison ID", readonly=True)

    def action_create_stock_picking(self):
        for record in self:
            if not record.prescription_line_ids:
                raise UserError("Aucune ligne de prescription disponible pour créer une livraison.")

            if record.submit_state != 'draft':
                raise UserError("Cette prescription a déjà été soumise.")

            # Rechercher l'emplacement WH/Stock (source)
            stock_location = self.env.ref('stock.stock_location_stock')

            # Rechercher l'emplacement Client (destination)
            customer_location = self.env.ref('stock.stock_location_customers')
            if not customer_location:
                raise UserError("L'emplacement client n'est pas configuré. Veuillez vérifier votre configuration.")

            # Créer le picking
            picking_vals = {
                'origin': record.name,
                'partner_id': record.patient_id.id,  # Assurez-vous que 'patient_id' est correct
                'location_id': stock_location.id,
                'location_dest_id': customer_location.id,
                'picking_type_id': self.env.ref('stock.picking_type_out').id,  # Type de picking (sortant)
            }
            picking = self.env['stock.picking'].create(picking_vals)

            # Créer les mouvements de stock
            for line in record.prescription_line_ids:
                move_vals = {
                    'name': line.product_id.display_name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': stock_location.id,  # Emplacement source
                    'location_dest_id': customer_location.id,  # Emplacement destination
                    'picking_id': picking.id,  # Associer le picking
                }
                self.env['stock.move'].create(move_vals)

            # Lier le picking à l'ordre de prescription et changer l'état
            record.x_studio_livraison_id = picking.id
            record.submit_state = 'submitted'
