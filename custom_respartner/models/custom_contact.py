import logging
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"
    activity_area = fields.Selection([("cash","Cash"),("card","Card")], string="Secteur d'activité")