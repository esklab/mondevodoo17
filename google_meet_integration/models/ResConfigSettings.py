from odoo import api, models, http, fields, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    google_client_id = fields.Char(string="Google Client ID")
    google_client_secret = fields.Char(string="Google Client Secret")
    google_redirect = fields.Char(string="Google Redirect Uri")

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('google_client_id', self.google_client_id)
        self.env['ir.config_parameter'].set_param('google_client_secret', self.google_client_secret)
        self.env['ir.config_parameter'].set_param('google_redirect', self.google_redirect)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        google_client_id = self.env['ir.config_parameter'].sudo().get_param('google_client_id')
        google_client_secret = self.env['ir.config_parameter'].sudo().get_param('google_client_secret')
        google_redirect = self.env['ir.config_parameter'].sudo().get_param('google_redirect')
        res.update(
            google_client_id=google_client_id,
            google_client_secret=google_client_secret,
            google_redirect=google_redirect,
        )
        return res
