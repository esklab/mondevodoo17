import logging
from datetime import datetime, timedelta
import requests
from odoo import models, http, fields, _
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

TIMEOUT = 20

class Users(models.Model):
    _inherit = "res.users"

    is_authenticated_google = fields.Boolean()
    google_access_token = fields.Char(string="Google meet Token")
    google_refresh_token = fields.Char()
    google_authorization_code = fields.Char()
    google_access_token_expiration = fields.Datetime(string="Expires In")

    def google_meet_authenticate(self):
        """Method for authentication"""
        google_client_id = self.env['ir.config_parameter'].sudo().get_param('google_client_id')
        google_client_secret = self.env['ir.config_parameter'].sudo().get_param('google_client_secret')
        google_redirect = self.env['ir.config_parameter'].sudo().get_param('google_redirect')
        if not google_client_id:
            raise ValidationError("Please Enter Client ID")
        client_id = google_client_id
        if not google_client_secret:
            raise ValidationError("Please Enter Client Secret")
        redirect_url = google_redirect
        calendar_scope = 'https://www.googleapis.com/auth/calendar'
        calendar_event_scope = 'https://www.googleapis.com/auth/calendar.events'
        url = (
            "https://accounts.google.com/o/oauth2/v2/auth?response_type=code"
            "&access_type=offline&client_id={}&redirect_uri={}&scope={}+{} "
        ).format(client_id, redirect_url, calendar_scope,
                 calendar_event_scope)
        return {
            "type": 'ir.actions.act_url',
            "url": url,
            "target": "new"
        }


    def google_meet_refresh_token(self):
        """Method to get the refresh token"""

        google_client_id = self.env['ir.config_parameter'].sudo().get_param('google_client_id')
        google_client_secret = self.env['ir.config_parameter'].sudo().get_param('google_client_secret')
        google_redirect = self.env['ir.config_parameter'].sudo().get_param('google_redirect')
        if not google_client_id:
            raise UserError(_('Client ID is not yet configured.'))
        client_id = google_client_id
        if not google_client_secret:
            raise UserError(
                _('Client Secret is not yet configured.'))
        client_secret = google_client_secret
        if not self.google_refresh_token:
            raise UserError(
                _('Refresh Token is not yet configured.'))
        refresh_token = self.google_refresh_token
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        response = requests.post(
            'https://accounts.google.com/o/oauth2/token', data=data,
            headers={
                'content-type': 'application/x-www-form-urlencoded'},
            timeout=TIMEOUT)
        if response.json() and response.json().get('access_token'):
            self.write({
                'google_access_token':
                    response.json().get('access_token'),
            })
        else:
            raise UserError(
                _('Something went wrong during the token generation.'
                  ' Please request again an authorization code.')
            )
