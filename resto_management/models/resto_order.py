from odoo import models, fields, api

class RestaurantOrder(models.Model):
    _name = 'resto.order'
    _description = 'Commandes du Restaurant'

    table_id = fields.Many2one("resto.table", string="Table")
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('served', 'Servie'),
        ('paid', 'Payée'),
    ], default="draft", tracking=True)
    total_amount = fields.Float(string='Montant Total', compute='_compute_total', store=True)
    order_line_ids = fields.One2many('resto.order.line', 'order_id', string='Lignes de Commande')
    pos_order_id = fields.Many2one("pos.order", string="Commande PoS", readonly=True)

    @api.depends('order_line_ids.subtotal')
    def _compute_total(self):
        for order in self:
            order.total_amount = sum(order.order_line_ids.mapped('subtotal'))

    def action_send_to_pos(self):
        """Créer une commande PoS à partir de la commande Restaurant"""
        customer = self.env['res.partner'].search([('name', '=', 'Client du Restaurant')], limit=1)
        if not customer:
            customer = self.env['res.partner'].create({'name': 'Client du Restaurant'})

        pos_order = self.env['pos.order'].create({
            'partner_id': customer.id,
            'amount_total': self.total_amount,
        })

        for line in self.order_line_ids:
            self.env['pos.order.line'].create({
                'order_id': pos_order.id,
                'product_id': line.product_id.id,
                'qty': line.quantity,
                'price_unit': line.price_unit,
            })

        self.pos_order_id = pos_order.id
        self.state = 'paid'

class RestaurantOrderLine(models.Model):
    _name = 'resto.order.line'
    _description = 'Ligne de Commande du Restaurant'

    order_id = fields.Many2one('resto.order', string='Commande', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Produit', required=True)
    quantity = fields.Integer(string='Quantité', default=1, required=True)
    price_unit = fields.Float(string='Prix Unitaire', required=True)
    subtotal = fields.Float(string='Sous-total', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Met à jour le prix unitaire en fonction du produit sélectionné"""
        if self.product_id:
            self.price_unit = self.product_id.lst_price
