# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class CustomLaboratory(models.Model):
    _inherit = 'acs.laboratory.request'

    laboratory_group_ids = fields.Many2many('laboratory.group', string='Test Groups')

    @api.onchange('laboratory_group_ids')
    def onchange_laboratory_group(self):
        test_line_ids = []
        if self.laboratory_group_ids:
            for group in self.laboratory_group_ids:
                for line in group.line_ids:
                    test_line_ids.append((0, 0, {
                        'test_id': line.test_id.id,
                        'instruction': line.instruction,
                        'sale_price': line.sale_price,
                    }))
            self.line_ids = test_line_ids
