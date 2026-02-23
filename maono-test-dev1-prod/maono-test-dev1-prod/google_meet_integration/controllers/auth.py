import requests
import datetime
from odoo import http
from odoo import _
from odoo.exceptions import UserError
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class GoogleMeetAuth(http.Controller):
    """Controller handling Google Meet authentication for Odoo users."""
    @http.route('/google_meet_authentication', type="http", auth="public",
                website=True)
    def get_auth_code(self, **kw):
        """  Retrieve the authentication code for Google Meet."""
        user_id = request.uid
        user = http.request.env['res.users'].sudo().search(
            [('id', '=', user_id)], limit=1)
        if kw.get('code'):
            user.write({'google_authorization_code': kw.get('code')})
            #client_id = "248884326645-j4ruojhnerm3k62qhdt4r1rllimp3a2p.apps.googleusercontent.com" #company_id.hangout_client_id
            #client_secret = "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" #company_id.hangout_client_secret
            #redirect_uri = "https://maono01-maono-test-dev11-charlestest-13135922.dev.odoo.com/google_account/authentication" #company_id.hangout_redirect_uri

            google_client_id = "248884326645-j4ruojhnerm3k62qhdt4r1rllimp3a2p.apps.googleusercontent.com" # self.env['ir.config_parameter'].sudo().get_param('google_client_id')
            google_client_secret = "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" # self.env['ir.config_parameter'].sudo().get_param('google_client_secret')
            google_redirect = "https://maono01-maono-test-dev11-charlestest-13135922.dev.odoo.com/google_meet_authentication" #self.env['ir.config_parameter'].sudo().get_param('google_redirect')

            data = {
                'code': kw.get('code'),
                'client_id': google_client_id,
                'client_secret': google_client_secret,
                'redirect_uri': google_redirect,
                'grant_type': 'authorization_code'
            }
            response = requests.post(
                'https://accounts.google.com/o/oauth2/token', data=data,
                headers={
                    'content-type': 'application/x-www-form-urlencoded'})
            if response.json() and response.json().get('access_token'):
                user.write({
                    'google_access_token':
                        response.json().get('access_token'),
                    'is_authenticated_google':
                        True,
                    'google_access_token_expiration':
                        datetime.datetime.now() + datetime.timedelta(
                            seconds=response.json().get('expires_in')),
                    'google_refresh_token':
                        response.json().get('access_token'),
                })
                return "Authentication Success. You Can Close this window"
            else:

                _logger.info("error here: %s", response.json())

                raise UserError(
                    _('Something went wrong during the token generation.'
                      'Maybe your Authorization Code is invalid')
                )