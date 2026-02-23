import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def create(self, vals):
        _logger.info("Creating a new company with values: %s", vals)
        company = super(ResCompany, self).create(vals)
        _logger.info("Company created with ID: %s and name: %s", company.id, company.name)
        
        # Paramètres par défaut à définir pour chaque nouvelle société
        default_params = {
            'account.default_chart_template_id': self.env['ir.config_parameter'].sudo().get_param('account.default_chart_template_id'),
            # Ajoutez d'autres paramètres par défaut si nécessaire
        }

        # Appliquer chaque paramètre par défaut à la société créée
        for param_key, param_value in default_params.items():
            try:
                if param_value:
                    self.env['ir.config_parameter'].sudo().set_param(param_key, param_value, company_id=company.id)
                    _logger.info("Parameter %s set to %s for company ID: %s", param_key, param_value, company.id)
            except Exception as e:
                _logger.error("Error setting parameter %s for company ID: %s: %s", param_key, company.id, str(e))

        return company


"""    @api.model
    def create(self, vals):
        _logger.info("Creating a new company with values: %s", vals)
        company = super(ResCompany, self).create(vals)
        _logger.info("Company created with ID: %s and name %s", company.id,company.name)
        settings = self.env['res.config.settings'].create({
                'company_id': company.id,
                'chart_template': 'tg  ',
                'has_accounting_entries':'True'
            })
        settings.execute()
        _logger.info("Chart of accounts activated for company: %s and name %s", company.id,company.name)

        return company
"""
        

        