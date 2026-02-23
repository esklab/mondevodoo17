# -*- coding: utf-8 -*-
###################################################################################
#
#    inteslar software trading llc.
#    Copyright (C) 2018-TODAY inteslar (<https://www.inteslar.com>).
#    Author:   (<https://www.inteslar.com>)
#
###################################################################################
from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    route_ids = fields.One2many('freight.route', 'picking_id', string="Freight Routes")
    freight_operation_id = fields.Many2one(
        'freight.operation',
        'Freight Operation',
        copy=False,
    )
