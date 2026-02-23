# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    appraisal_template_id = fields.Many2one(related='company_id.appraisal_template_id', readonly=False, check_company=True)