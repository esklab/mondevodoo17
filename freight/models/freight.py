# -*- coding: utf-8 -*-
###################################################################################
#
#    inteslar software trading llc.
#    Copyright (C) 2018-TODAY inteslar (<https://www.inteslar.com>).
#    Author:   (<https://www.inteslar.com>)
#
###################################################################################
import logging
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError
from random import choice
from string import digits
from json import dumps
import json

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    shipper = fields.Boolean('Shipper')
    consignee = fields.Boolean('Consignee')
    agent = fields.Boolean('Agent')

class CustomerInvoice(models.Model):
    _inherit = 'account.move'

    freight_operation_id = fields.Many2one('freight.operation', string='Freight operation')

class ShipmentStage(models.Model):
    _name = 'shipment.stage'
    _description = 'shipment Stage'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)

class ShipmentLog(models.Model):
    _name = 'shipment.log'
    _description = 'Shipment Stage'

    date = fields.Date('Date')
    location = fields.Char(required=True, translate=True)
    description = fields.Char(required=True, translate=True)
    shipment_id = fields.Many2one('freight.operation', string='Shipment ID')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    freight_id = fields.Many2one('freight.operation', string='Freight')


class FreightOperation(models.Model):
    _name = 'freight.operation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Freight Operation'

    def _get_default_stage_id(self):
        return self.env['shipment.stage'].search([], order='sequence', limit=1)

    def _default_random_barcode(self):
        return "".join(choice(digits) for i in range(8))

    barcode = fields.Char(string="Barcode", help="ID used for shipment identification.",
                          default=_default_random_barcode, copy=False)
    color = fields.Integer('Color')
    stage_id = fields.Many2one('shipment.stage', 'Stage',default=_get_default_stage_id, group_expand='_read_group_stage_ids')
    name = fields.Char(string='Name', copy=False)
    direction = fields.Selection(([('import','Import'),('export','Export')]), string='Direction')
    transport = fields.Selection(([('air','Air'),('ocean','Ocean'),('land','Land')]), string='Transport')
    operation = fields.Selection([('direct', 'Direct'), ('house', 'House'), ('master', 'Master')], string='Operation')
    ocean_shipment_type = fields.Selection(([('fcl','FCL'),('lcl','LCL')]), string='Ocean Shipment Type')
    inland_shipment_type = fields.Selection(([('ftl','FTL'),('ltl','LTL')]), string='Inland Shipment Type')
    shipper_id = fields.Many2one('res.partner', 'Shipper')
    consignee_id = fields.Many2one('res.partner', 'Consignee')
    source_location_id = fields.Many2one('freight.port', 'Source Location', index=True, required=True)
    destination_location_id = fields.Many2one('freight.port', 'Destination Location', index=True, required=True)
    obl = fields.Char('OBL', help='Original Bill Of Landing')
    shipping_line_id = fields.Many2one('res.partner','Shipping Line')
    voyage_no = fields.Char('Voyage No')
    vessel_id = fields.Many2one('freight.vessel', 'Vessel')
    mawb_no = fields.Char('MAWB No')
    airline_id = fields.Many2one('freight.airline', 'Airline')
    flight_no = fields.Char('Flight No')
    datetime = fields.Datetime('Date')
    truck_ref = fields.Char('CMR/RWB#/PRO#:')
    trucker = fields.Many2one('freight.trucker', 'Trucker')
    trucker_id = fields.Many2one('fleet.vehicle', 'Trucker ')
    trucker_number = fields.Char('Trucker No')
    agent_id = fields.Many2one('res.partner', 'Agent')
    operator_id = fields.Many2one('res.users', 'User')
    freight_pc = fields.Selection(([('collect','Collect'),('prepaid','Prepaid')]),string="Freight PC")
    other_pc = fields.Selection(([('collect','Collect'),('prepaid','Prepaid')]),string="Other PC")
    notes = fields.Text('Notes')
    dangerous_goods = fields.Boolean('Dangerous Goods')
    dangerous_goods_notes = fields.Text('Dangerous Goods Info')
    move_type = fields.Many2one('freight.move.type', 'Move Type')
    tracking_number = fields.Char('Tracking Number')
    declaration_number = fields.Char('Declaration Number')
    declaration_date = fields.Date('Declaration Date')
    custom_clearnce_date = fields.Datetime('Customs Clearance Date')
    freight_orders = fields.One2many('freight.order', 'shipment_id')
    freight_packages = fields.One2many('freight.package.line', 'shipment_id')
    freight_services = fields.One2many('freight.service', 'shipment_id')

    incoterm = fields.Many2one('freight.incoterms','Incoterm')
    freight_routes = fields.One2many('freight.route', 'shipment_id')
    freight_log = fields.One2many('shipment.log', 'shipment_id')
    parent_id = fields.Many2one('freight.operation', 'Parent')
    shipments_ids = fields.One2many('freight.operation', 'parent_id')
    service_count = fields.Float('Services Count', compute='_compute_invoice')
    invoice_count = fields.Float('Invoice Count', compute='_compute_invoice')
    vendor_bill_count = fields.Float('Vendor Bill Count', compute='_compute_invoice')
    total_invoiced = fields.Float('Total Invoiced(Receivables', compute='compute_total_amount')
    total_bills = fields.Float('Total Bills(Payables)', compute='compute_total_amount')
    margin = fields.Float("Margin", compute='compute_total_amount')
    invoice_residual = fields.Float('Invoice Residual',compute='compute_total_amount')
    bills_residual = fields.Float('Bills Residual', compute='compute_total_amount')
    invoice_paid_amount = fields.Float('Invoice', compute='compute_total_amount')
    bills_paid_amount = fields.Float('Bills', compute='compute_total_amount')
    actual_margin = fields.Float('Actual Margin', compute='compute_total_amount')
    sale_orders = fields.One2many('sale.order', 'freight_id')
    booking_id = fields.Many2one('freight.booking')
    service_quote_count = fields.Float('Quote Count', compute='_compute_invoice')
    service_booking_count = fields.Float('Booking Count', compute='_compute_invoice')
    operation_picking_ids = fields.One2many(
        'stock.picking',
        'freight_operation_id',
        string='Pickings'
    )
    operation_product_id = fields.Many2one(
        'product.product',
        'Shipment Product'
    )
    freight_nbr_moves_in = fields.Integer(
        compute='_compute_freight_nbr_moves',
        compute_sudo=False,
        help="Number of incoming stock moves in the past 12 months"
    )
    freight_nbr_moves_out = fields.Integer(
        compute='_compute_freight_nbr_moves',
        compute_sudo=False,
        help="Number of outgoing stock moves in the past 12 months"
    )
    insurance_transport = fields.Boolean('Assurance transport')#added
    insurance_policy = fields.Char('N° Police d’Assurance')#added
    delivery_mode = fields.Selection(
        selection=[('port_port', 'Port à Port'), ('port_door', 'Port à Domicile')],
        string="Mode de livraison"
    )#added

    # Contrainte pour l'assurance
    @api.constrains('insurance_transport', 'insurance_policy')
    def _check_insurance(self):
        for rec in self:
            if rec.insurance_transport and not rec.insurance_policy:
                raise ValidationError("Le numéro de police est obligatoire lorsque l'assurance est activée !")
    
    def _compute_freight_nbr_moves(self):
        res = defaultdict(dict)
        incoming_moves = self.env['stock.move.line'].read_group([
                ('product_id', 'in', self.operation_product_id.ids),
                ('state', '=', 'done'),
                ('picking_code', '=', 'incoming'),
                ('date', '>=', fields.Datetime.now() - relativedelta(years=1))
            ], ['product_id'], ['product_id'])
        outgoing_moves = self.env['stock.move.line'].read_group([
                ('product_id', 'in', self.operation_product_id.ids),
                ('state', '=', 'done'),
                ('picking_code', '=', 'outgoing'),
                ('date', '>=', fields.Datetime.now() - relativedelta(years=1))
            ], ['product_id'], ['product_id'])
        for move in incoming_moves:
            res[move['product_id'][0]]['moves_in'] = int(move['product_id_count'])
        for move in outgoing_moves:
            res[move['product_id'][0]]['moves_out'] = int(move['product_id_count'])
        for operation in self:
            operation_res = res.get(operation.operation_product_id.id) or {}
            operation.freight_nbr_moves_in = operation_res.get('moves_in', 0)
            operation.freight_nbr_moves_out = operation_res.get('moves_out', 0)

    @api.depends('freight_services')
    def compute_total_amount(self):
        for order in self:
            invoices = self.env['account.move'].sudo().search([('freight_operation_id', '=', order.id), ('move_type', '=', 'out_invoice'),('state', '=', 'posted')])
            invoice_amount = 0.0
            bill_amount = 0.0
            invoice_residual = 0.0
            bills_residual = 0.0
            invoice_paid_amount = 0.0
            bills_paid_amount = 0.0
            for invoice in invoices:
                invoice_amount+=invoice.amount_total
                invoice_residual+= invoice.amount_residual
                reconciled_payments_widget_vals = invoice.invoice_payments_widget
                if reconciled_payments_widget_vals:
                    paid_amount_dict = {vals['move_id']: vals['amount'] for vals in reconciled_payments_widget_vals['content']}
                else:
                    paid_amount_dict = 0.0
                invoice_paid_amount += sum(list(paid_amount_dict.values())) if type(paid_amount_dict) == dict else 0.0

            bills = self.env['account.move'].sudo().search([('freight_operation_id', '=', order.id), ('move_type', '=', 'in_invoice'),('state', '=', 'posted')])
            for bill in bills:
                bill_amount+=bill.amount_total
                bills_residual+= bill.amount_residual
                reconciled_payments_widget_vals_bill = bill.invoice_payments_widget
                if reconciled_payments_widget_vals_bill:
                    paid_bill_amount_dict = {vals['move_id']: vals['amount'] for vals in reconciled_payments_widget_vals_bill['content']}
                else:
                    paid_bill_amount_dict = 0.0
                bills_paid_amount += sum(list(paid_bill_amount_dict.values())) if type(paid_bill_amount_dict) == dict else 0.0

            order.total_invoiced = invoice_amount
            order.total_bills = bill_amount
            order.margin =  invoice_amount - bill_amount
            order.invoice_residual = invoice_residual
            order.invoice_paid_amount = invoice_paid_amount
            order.bills_residual = bills_residual
            order.bills_paid_amount = bills_paid_amount
            order.actual_margin = invoice_paid_amount - bills_paid_amount

    @api.model
    def _read_group_stage_ids(self,stages,domain,order):
        stage_ids = self.env['shipment.stage'].search([])
        return stage_ids

    @api.depends('freight_services')
    def _compute_invoice(self):
        for order in self:
            order.service_count = len(order.freight_services)
            order.service_quote_count = len(order.sale_orders)
            order.invoice_count = self.env['account.move'].sudo().search_count([('freight_operation_id','=', order.id),('move_type','=', 'out_invoice')])
            order.vendor_bill_count  = self.env['account.move'].sudo().search_count([('freight_operation_id','=', order.id),('move_type','=', 'in_invoice')])
            order.service_booking_count = 1 if self.booking_id else 0

    @api.depends('freight_routes.picking_id')
    def _compute_picking_ids(self):
        for rec in self:
            rec.picking_ids = rec.freight_routes.picking_id

    def button_services(self):
        services = self.mapped('freight_services')
        action = self.env["ir.actions.actions"]._for_xml_id("freight.view_freight_service_action")
        action['context'] = {'default_shipment_id': self.id}
        action['domain'] = [('id', 'in', services.ids)]
        return action

    def button_services_quotes(self):
        action = {
            'name': _('Sales Order(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'target': 'current',
        }
        action['context'] = {'default_freight_id': self.id}
        sale_order_ids = self.sale_orders.ids
        if len(sale_order_ids) == 1:
            action['res_id'] = sale_order_ids[0]
            action['view_mode'] = 'form'
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', sale_order_ids)]
        return action

    def button_services_bookings(self):
        action = {
            'name': _('Booking'),
            'type': 'ir.actions.act_window',
            'res_model': 'freight.booking',
            'target': 'current',
        }
        action['domain'] =[('id', '=', self.booking_id.id)]
        booking_id = self.booking_id.id
        action['res_id'] = booking_id
        action['view_mode'] = 'form'
        return action


    def button_customer_invoices(self):
        invoices = self.env['account.move'].sudo().search([('freight_operation_id', '=', self.id), ('move_type', '=', 'out_invoice')])
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['context'] = {'default_freight_operation_id': self.id,'default_move_type': 'out_invoice',}
        if len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action['domain'] = [('id', 'in', invoices.ids)]
        return action

    def button_vendor_bills(self):
        invoices = self.env['account.move'].sudo().search([('freight_operation_id', '=', self.id), ('move_type', '=', 'in_invoice')])
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_invoice_type")
        action['context'] = {'default_freight_operation_id': self.id, 'default_move_type': 'in_invoice', }
        if len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action['domain'] = [('id', 'in', invoices.ids)]
        return action

    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
            if values.get('operation') == 'master':
                values['name'] = self.env['ir.sequence'].next_by_code('operation.master') or _('New')
            elif values.get('operation') == 'house':
                values['name'] = self.env['ir.sequence'].next_by_code('operation.house') or _('New')
            elif values.get('operation') == 'direct':
                values['name'] = self.env['ir.sequence'].next_by_code('operation.direct') or _('New')
        if values.get('name', False) and not values.get('tracking_number', False):
            values['tracking_number'] = values.get('name', False)
        id_data = super(FreightOperation, self).create(values).id
        id = self.env['freight.operation'].browse(id_data)
        if id.transport == 'air':
            self.env['freight.route'].create({'source_location_id': id.source_location_id.id,
                                              'destination_location_id': id.destination_location_id.id,
                                              'main_carriage': True,
                                              'transport':id.transport,
                                              'mawb_no': id.mawb_no,
                                              'airline_id': id.airline_id.id,
                                              'flight_no': id.flight_no,
                                              'shipment_id': id.id})
        if id.transport == 'ocean':
            self.env['freight.route'].create({'source_location_id': id.source_location_id.id,
                                              'destination_location_id': id.destination_location_id.id,
                                              'main_carriage': True,
                                              'transport':id.transport,
                                              'shipping_line_id': id.shipping_line_id.id,
                                              'vessel_id': id.vessel_id.id,
                                              'obl': id.obl,
                                              'shipment_id': id.id})
        if id.transport == 'land':
            self.env['freight.route'].create({'source_location_id': id.source_location_id.id,
                                              'destination_location_id': id.destination_location_id.id,
                                              'main_carriage': True,
                                              'transport':id.transport,
                                              'truck_ref': id.truck_ref,
                                              'trucker': id.trucker.id,
                                              'trucker_number': id.trucker_number,
                                              'shipment_id': id.id})
        if 'default_booking_id' in self._context.keys():
            book = self.env['freight.booking'].browse(self._context.get('default_booking_id'))
            book.freight_id = id.id
        return id

    @api.depends('transport')
    @api.onchange('source_location_id')
    def onchange_source_location_id(self):
        for line in self:
            if line.transport == 'air':
                return {'domain': {'source_location_id': [('air', '=', True)]}}
            elif line.transport == 'ocean':
                return {'domain': {'source_location_id': [('ocean', '=', True)]}}
            elif line.transport == 'land':
                return {'domain': {'source_location_id': [('land', '=', True)]}}

    @api.depends('transport')
    @api.onchange('destination_location_id')
    def onchange_destination_location_id(self):
        for line in self:
            if line.transport == 'air':
                return {'domain': {'destination_location_id': [('air', '=', True)]}}
            elif line.transport == 'ocean':
                return {'domain': {'destination_location_id': [('ocean', '=', True)]}}
            elif line.transport == 'land':
                return {'domain': {'destination_location_id': [('land', '=', True)]}}

    @api.depends('transport')
    @api.onchange('trucker_id')
    def _onchange_trucker_id(self):
        if self.trucker_id:
            self.trucker_number = self.trucker_id.license_plate

    def generate_from_the_orders(self):
        for line in self:
            packages = []
            for order in line.freight_orders:
                packages.append((0, 0, {'name': order.name,
                                        'package':order.package.id,
                                        'qty': order.qty,
                                        'volume': order.volume,
                                        'gross_weight': order.gross_weight,
                                        'shipment_id':line.id,
                                        'type':order.type}))
            self.freight_packages.unlink()
            self.write({'freight_packages':packages})

    def action_view_freight_stock_move_lines(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_line_action")
        action['domain'] = [('product_id', '=', self.operation_product_id.id)]
        return action

class FreightTrucker(models.Model):
    _name = 'freight.trucker'
    _description = 'Freight Trucker'

    name = fields.Char(string='Name')

class FreightPackageLine(models.Model):
    _name = 'freight.package.line'
    _description = 'Freight Package Line'

    name = fields.Char(string='Description', required=True)
    transport = fields.Selection(([('air','Air'),('ocean','Ocean'),('land','Land')]), string='Transport')
    shipment_id = fields.Many2one('freight.operation', 'Shipment ID')
    package = fields.Many2one('freight.package', 'Package', required=True)
    type = fields.Selection(([('dry','Dry'),('reefer','Reefer')]),string="Operation")
    volume = fields.Float('Volume (CBM)')
    gross_weight = fields.Float('Gross Weight (KG)')
    qty = fields.Float('Quantity', required=True)
    harmonize = fields.Char('Harmonize')
    temperature = fields.Char('Temperature')
    vgm = fields.Char('VGM', help='Verified gross mass')
    carrier_seal = fields.Char('Carrier Seal')
    shipper_seal = fields.Char('Shipper Seal')
    reference = fields.Char('Reference')
    dangerous_goods = fields.Boolean('Dangerous Goods')
    class_number = fields.Char('Class Number')
    un_number = fields.Char('UN Number', help='UN numbers are four-digit numbers that identify hazardous materials, and articles in the framework of international transport')
    Package_group = fields.Char('Packaging Group:')
    imdg_code = fields.Char('IMDG Code', help='International Maritime Dangerous Goods Code')
    flash_point = fields.Char('Flash Point')
    material_description = fields.Text('Material Description')
    freight_item_lines = fields.One2many('freight.item.line', 'package_line_id')
    route_id = fields.Many2one('freight.route', 'Route')

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.context.get('shipment_id_domain', False):
            args.append(('shipment_id', '=', self.env.context.get('shipment_id_domain', False)))
        return super(FreightPackageLine, self).search(args, offset=offset, limit=limit, order=order, count=count)

    @api.onchange('package')
    def onchange_package_id(self):
        for line in self:
            if line.shipment_id.transport == 'air':
                return {'domain': {'package': [('air', '=', True)]}}
            if line.shipment_id.transport == 'ocean':
                return {'domain': {'package': [('ocean', '=', True)]}}
            if line.shipment_id.transport == 'land':
                return {'domain': {'package': [('land', '=', True)]}}

class FreightItemLine(models.Model):
    _name = 'freight.item.line'
    _description = 'Freight Item Line'

    name = fields.Char(string='Description')
    package_line_id = fields.Many2one('freight.package.line', 'Shipment ID')
    package = fields.Many2one('freight.package', 'Package')
    type = fields.Selection(([('dry','Dry'),('reefer','Reefer')]),string="Operation")
    volume = fields.Float('Volume (CBM)')
    gross_weight = fields.Float('Gross Weight (KG)')
    qty = fields.Float('Quantity')

    @api.onchange('package')
    def onchange_package_id(self):
        for line in self:
            if line.package_line_id.shipment_id.transport == 'air':
                return {'domain': {'package': [('air', '=', True)]}}
            if line.package_line_id.shipment_id.transport == 'ocean':
                return {'domain': {'package': [('ocean', '=', True)]}}
            if line.package_line_id.shipment_id.transport == 'land':
                return {'domain': {'package': [('land', '=', True)]}}

class FreightOrder(models.Model):
    _name = 'freight.order'
    _description = 'Freight Order'

    shipment_id = fields.Many2one('freight.operation', 'Shipment ID')
    transport = fields.Selection(([('air','Air'),('ocean','Ocean'),('land','Land')]), string='Transport')
    name = fields.Char(string='Description', required=True)
    package = fields.Many2one('freight.package', 'Package', required=True)
    type = fields.Selection(([('dry','Dry'),('reefer','Reefer')]),string="Operation")
    volume = fields.Float('Volume (CBM)')
    gross_weight = fields.Float('Gross Weight (KG)')
    qty = fields.Float('Quantity')

    @api.onchange('package')
    def onchange_package_id(self):
        for line in self:
            if line.shipment_id.transport == 'air':
                return {'domain': {'package': [('air', '=', True)]}}
            if line.shipment_id.transport == 'ocean':
                return {'domain': {'package': [('ocean', '=', True)]}}
            if line.shipment_id.transport == 'land':
                return {'domain': {'package': [('land', '=', True)]}}

class FreightService(models.Model):
    _name = 'freight.service'
    _description = 'Freight Service'

    service_id = fields.Many2one('product.product', 'Service', domain="[('type','=','service')]")
    currency_id = fields.Many2one('res.currency', 'Currency')
    name = fields.Char(string='Description')
    cost = fields.Float('Cost')
    sale = fields.Float('Sale')
    qty = fields.Float('Quantity')
    partner_id = fields.Many2one('res.partner', 'Vendor')
    route_id = fields.Many2one('freight.route', 'Route')
    shipment_id = fields.Many2one('freight.operation', 'Shipment ID')
    customer_invoice = fields.Many2one('account.move')
    vendor_invoice = fields.Many2one('account.move')
    invoiced = fields.Boolean('Invoiced')
    vendor_invoiced = fields.Boolean('Vendor Invoiced')

class FreightRoute(models.Model):
    _name = 'freight.route'
    _description = 'Freight Route'

    name=fields.Char('Description', compute='compute_name')
    type = fields.Selection([('pickup', 'Pickup'), ('oncarriage', 'On Carriage'), ('precarriage', 'Pre Carriage'),('delivery', 'Delivery'), ('to_warehouse', 'To Warehouse'), ('from_warehouse', 'From Warehouse')], string='Type')
    shipment_id = fields.Many2one('freight.operation', 'Shipment ID')
    transport = fields.Selection([('air','Air'),('ocean','Ocean'),('land','Land')], string='Transport')
    ocean_shipment_type = fields.Selection([('fcl','FCL'),('lcl','LCL')], string='Ocean Shipment Type')
    inland_shipment_type = fields.Selection([('ftl','FTL'),('ltl','LTL')], string='Inland Shipment Type')
    shipper_id = fields.Many2one('res.partner', 'Shipper')
    consignee_id = fields.Many2one('res.partner', 'Consignee')
    source_location_id = fields.Many2one('freight.port', 'Source Location')
    destination_location_id = fields.Many2one('freight.port', 'Destination Location')
    obl = fields.Char('OBL', help='Original Bill Of Lading')
    shipping_line_id = fields.Many2one('res.partner','Shipping Line')
    voyage_no = fields.Char('Voyage No')
    vessel_id = fields.Many2one('freight.vessel', 'Vessel')
    mawb_no = fields.Char('MAWB No')
    airline_id = fields.Many2one('freight.airline', 'Airline')
    flight_no = fields.Char('Flight No')
    datetime = fields.Datetime('Date')
    truck_ref = fields.Char('CMR/RWB#/PRO#:')
    trucker = fields.Many2one('freight.trucker', 'Trucker')
    trucker_id = fields.Many2one('fleet.vehicle', 'Trucker ')
    trucker_number = fields.Char(string='Trucker No')
    etd = fields.Datetime('ETD')
    eta = fields.Datetime('ETA')
    atd = fields.Datetime('ATD')
    ata = fields.Datetime('ATA')
    package_ids = fields.One2many('freight.package.line', 'route_id')
    freight_services = fields.One2many('freight.service', 'route_id')
    main_carriage = fields.Boolean('Main Carriage')
    picking_id = fields.Many2one(
        'stock.picking',
        string='Picking'
    )
    from_warehouse_id = fields.Many2one(
        'stock.warehouse',
        'From Warehouse',
    )
    to_warehouse_id = fields.Many2one(
        'stock.warehouse',
        'To Warehouse',
    )
    from_location_id = fields.Many2one(
        'stock.location',
        'From Location'
    )
    to_location_id = fields.Many2one(
        'stock.location',
        'To Location'
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Address'
    )
    shipping_date = fields.Datetime(
        'Shipping  Date'
    )
    picking_group_id = fields.Many2one(
        'procurement.group',
        string="Procurement Group",
        copy=False
    )
    
    @api.depends('transport')
    @api.onchange('trucker_id')
    def _onchange_trucker_id(self):
        if self.trucker_id:
            self.trucker_number = self.trucker_id.license_plate

    @api.model
    def create(self, values):
        id = super(FreightRoute, self).create(values)
        id.freight_services.write({'shipment_id':id.shipment_id.id})
        return id

    def write(self, vals):
        res = super(FreightRoute, self).write(vals)
        self.freight_services.write({'shipment_id': self.shipment_id.id})
        return res

    def compute_name(self):
        for line in self:
            if line.main_carriage:
                line.name = 'Main carriage'
            elif line.type:
                line.name = line.type
            else:
                line.name = '/'

    def _get_picking_type_in(self):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id', '=', self.to_warehouse_id.id),('warehouse_id.company_id', '=', self.env.company.id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), '|', ('warehouse_id', '=', self.to_warehouse_id.id), ('warehouse_id', '=', False)])
        return picking_type[:1]

    def _get_picking_type_out(self):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing'), ('warehouse_id', '=', self.from_warehouse_id.id),('warehouse_id.company_id', '=', self.env.company.id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing'), '|', ('warehouse_id', '=', self.from_warehouse_id.id), ('warehouse_id', '=', False)])
        return picking_type[:1]
    
    def _get_destination_location(self, picking_type_id):
        self.ensure_one()
        return picking_type_id.default_location_dest_id.id
    
    def _get_src_location(self, picking_type_id):
        self.ensure_one()
        return picking_type_id.default_location_src_id.id

    #                  CREATE STOCK PICKING IN

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty):
        self.ensure_one()
#        self._check_orderpoint_picking_type()
        product = self.shipment_id.operation_product_id.with_context(lang=self.env.user.lang)
        date_planned = self.shipping_date
        return {
            'name': (self.shipment_id.name or ''),
            'product_id': product.id,
            'date': date_planned,
            'date_deadline': date_planned,
            'location_id': self.partner_id.property_stock_supplier.id,
            'location_dest_id': self._get_destination_location(picking.picking_type_id),
            'picking_id': picking.id,
            'partner_id': self.partner_id.id,
            'move_dest_ids': [],
            'state': 'draft',
            'company_id': self.env.company.id,
            'price_unit': 1.0,
            'picking_type_id': picking.picking_type_id.id,
            'group_id': self.picking_group_id.id,
            'origin': self.shipment_id.name,
            'description_picking': product.description_pickingin or self.shipment_id.name,
            'warehouse_id': self.to_warehouse_id.id,
            'product_uom_qty': 1.0,
            'product_uom': product.uom_id.id,
        }

    def _create_operation_product(self):
        product = self.env['product.product'].create({
            'name': self.shipment_id.name,
            'shipment_ok': True,
            'detailed_type': 'product',
        })
        return product

    def action_create_stock_picking_in(self):
        self._check_stock_picking()
        StockPicking = self.env['stock.picking']

        if not self.shipment_id.operation_product_id:
            self.shipment_id.operation_product_id = self._create_operation_product()
        if not self.picking_group_id:
            self.picking_group_id = self.picking_group_id.create({
                'name': self.shipment_id.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s or Customer/Vendor is not set on Route", self.partner_id.name))

        picking_type_id = self._get_picking_type_in()
        pick_vals = {
            'picking_type_id': picking_type_id.id,
            'partner_id': self.partner_id.id,
            'user_id': False,
            'date': self.shipping_date,
            'origin': self.shipment_id.name,
            'location_dest_id': self._get_destination_location(picking_type_id),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.env.company.id,
            'freight_operation_id': self.shipment_id.id
        }
        picking = StockPicking.with_user(SUPERUSER_ID).create(pick_vals)
        move_vals = self._prepare_stock_move_vals(picking, 1.0, 1)
        move_id = self.env['stock.move'].create(move_vals)
        self.picking_id = picking.id

    #                  CREATE STOCK PICKING OUT 

    def _prepare_stock_move_vals_out(self, picking, price_unit, product_uom_qty):
        self.ensure_one()
#        self._check_orderpoint_picking_type()
        product = self.shipment_id.operation_product_id.with_context(lang=self.env.user.lang)
        date_planned = self.shipping_date
        return {
            'name': (self.shipment_id.name or ''),
            'product_id': product.id,
            'date': date_planned,
            'date_deadline': date_planned,
            'location_id': self._get_src_location(picking.picking_type_id),
            'location_dest_id': self.partner_id.property_stock_customer.id,
            'picking_id': picking.id,
            'partner_id': self.partner_id.id,
            'move_dest_ids': [],
            'state': 'draft',
            'company_id': self.env.company.id,
            'price_unit': 1.0,
            'picking_type_id': picking.picking_type_id.id,
            'group_id': self.picking_group_id.id,
            'origin': self.shipment_id.name,
            'description_picking': product.description_pickingin or self.shipment_id.name,
            'warehouse_id': self.from_warehouse_id.id,
            'product_uom_qty': 1.0,
            'product_uom': product.uom_id.id,
        }

    def action_create_stock_picking_out(self):
        self.ensure_one()
        self._check_stock_picking()
        StockPicking = self.env['stock.picking']

        if not self.shipment_id.operation_product_id:
            self.shipment_id.operation_product_id = self._create_operation_product()
        if not self.picking_group_id:
            self.picking_group_id = self.picking_group_id.create({
                'name': self.shipment_id.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_customer.id:
            raise UserError(_("You must set a Customer Location for this partner %s", self.partner_id.name))

        picking_type_id = self._get_picking_type_out()
        pick_vals = {
            'picking_type_id': picking_type_id.id,
            'partner_id': self.partner_id.id,
            'user_id': False,
            'date': self.shipping_date,
            'origin': self.shipment_id.name,
            'location_dest_id': self.partner_id.property_stock_customer.id,
            'location_id': self._get_src_location(picking_type_id),
            'company_id': self.env.company.id,
            'freight_operation_id': self.shipment_id.id
        }
        picking = StockPicking.with_user(SUPERUSER_ID).create(pick_vals)
        move_vals = self._prepare_stock_move_vals_out(picking, 1.0, 1)
        move_id = self.env['stock.move'].create(move_vals)
        self.picking_id = picking.id


    @api.model
    def create(self, values):
        res = super(FreightRoute, self).create(values)
        if res.type == 'to_warehouse':
            res.action_create_stock_picking_in()
        elif res.type == 'from_warehouse':
            res.action_create_stock_picking_out()
        return res

    @api.onchange('type')
    def onchange_type(self):
        for line in self:
            if line.type == 'precarriage':
                line.destination_location_id = line.shipment_id.source_location_id
            if line.type == 'oncarriage':
                line.source_location_id = line.shipment_id.destination_location_id

    def _check_stock_picking(self):
        if self.picking_id:
            raise ValidationError(_('You have already created stock picking once %s') %(self.picking_id.name))


class FreightRouteService(models.Model):
    _name = 'freight.route.service'
    _description = 'Freight Route Service'

    service_id = fields.Many2one('product.product', 'Service', domain="[('type','=','service')]")
    currency_id = fields.Many2one('res.currency', 'Currency')
    name = fields.Char(string='Description')
    cost = fields.Float('Cost')
    sale = fields.Float('Sale')
    partner_id = fields.Many2one('res.partner', 'Vendor')

class FreightPort(models.Model):
    _name = 'freight.port'
    _description = 'Freight Port'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    country = fields.Many2one('res.country', 'Country')
    state = fields.Many2one('res.country.state', 'Fed. State', domain="[('country_id', '=', country)]")
    air = fields.Boolean(string='Air')
    ocean = fields.Boolean(string='Ocean')
    land = fields.Boolean(string='Land')
    active = fields.Boolean(default=True, string='Active')

class FreightVessel(models.Model):
    _name = 'freight.vessel'
    _description = 'Freight Vessel'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    global_zone = fields.Char(string='Global Zone')
    country = fields.Many2one('res.country', 'Country')
    active = fields.Boolean(default=True, string='Active')

class FreightAirline(models.Model):
    _name = 'freight.airline'
    _description = 'Freight Airline'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    icao = fields.Char(string='ICAO')
    country = fields.Many2one('res.country', 'Country')
    active = fields.Boolean(default=True, string='Active')

class FreightIncoterms(models.Model):
    _name = 'freight.incoterms'
    _description = 'Freight Incoterms'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name',  help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")
    active = fields.Boolean(default=True, string='Active')

class FreightPackage(models.Model):
    _name = 'freight.package'
    _description = 'Freight Package'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    container = fields.Boolean('Is Container?')
    refrigerated = fields.Boolean('Refrigerated')
    active = fields.Boolean(default=True, string='Active')
    size = fields.Float('Size')
    volume = fields.Float('Volume')
    air = fields.Boolean(string='Air')
    ocean = fields.Boolean(string='Ocean')
    land = fields.Boolean(string='Land')

class FreightMoveType(models.Model):
    _name = 'freight.move.type'
    _description = 'Freight Move Type'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name')
    active = fields.Boolean(default=True, string='Active')
