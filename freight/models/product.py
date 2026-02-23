# -*- coding: utf-8 -*-
###################################################################################
#
#    inteslar software trading llc.
#    Copyright (C) 2018-TODAY inteslar (<https://www.inteslar.com>).
#    Author:   (<https://www.inteslar.com>)
#
###################################################################################
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shipment_ok = fields.Boolean(
        'Can be Shipped',
        copy=True
    )
