import json
import requests
import logging
from odoo import models, http, fields
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class GoogleOAuth2(models.AbstractModel):
    _name = 'google.oauth2'

    def authorize_google_credentials(self):
        # Get OAuth2 parameters from system parameters or module settings
        client_id = self.env['ir.config_parameter'].sudo().get_param('google.oauth2.client_id')
        client_secret = self.env['ir.config_parameter'].sudo().get_param('google.oauth2.client_secret')
        redirect_uri = http.request.env['google_meet_oauth_redirect'].route_url

        # Construct the authorization URL
        auth_url = 'https://accounts.google.com/o/oauth2/auth'
        auth_params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'openid profile email',
            'response_type': 'code',
        }
        redirect_url = "{}?{}".format(auth_url, '&'.join(['{}={}'.format(k, v) for k, v in auth_params.items()]))

        # Redirect the user's browser to the authorization URL
        return http.redirect_with_hash(redirect_url)

    @http.route('/google_meet/oauth2/callback', type='http', auth='public', website=True)
    def google_oauth2_callback(self, **kwargs):
        # Handle the callback from Google after the user has authorized the application

        # Extract the authorization code from the query parameters
        code = kwargs.get('code')

        # Exchange the authorization code for access and refresh tokens
        token_url = 'https://oauth2.googleapis.com/token'
        client_id = self.env['ir.config_parameter'].sudo().get_param('google.oauth2.client_id')
        client_secret = self.env['ir.config_parameter'].sudo().get_param('google.oauth2.client_secret')
        redirect_uri = http.request.env['google_meet_oauth_redirect'].route_url

        token_payload = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        try:
            token_response = requests.post(token_url, data=token_payload)
        except requests.exceptions.ConnectionError:
            _logger.exception("Could not establish the connection at %s", token_url)
            raise ValidationError(
                _("Could not establish the connection.")
                )

        except requests.exceptions.HTTPError:
            _logger.exception(
                "Invalid API request at %s", token_url
                )
            raise ValidationError(
                _(
                    "Webshipper: Invalid API request at %s",
                    token_url,
                    )
                )
        if token_response.status_code == 200:
            token_data = token_response.json()

            # Extract the access token and refresh token from the response
            access_token = token_data.get('access_token')
            refresh_token = token_data.get('refresh_token')
            # Store the expiration time for the access token
            expiration_time = datetime.now() + timedelta(seconds=token_data.get('expires_in'))

            # Store the access token and refresh token for the current user
            current_user = http.request.env.user
            current_user.write({
                'is_authenticated_google': True,
                'google_access_token': access_token,
                'google_refresh_token': refresh_token,
                'google_access_token_expiration': expiration_time,
            })

        # Redirect the user to the desired page after authentication
            return http.redirect('/web')
        else:
            response_error = token_response.json()
            error_body = token_response.json().get('error')
            if isinstance(error_body, str):
                error_message = "Error getting 'Access token' " + \
                    "\nStatus Code: %d \nReason: %s\n" % (
                        token_response.status_code, token_response.reason) + \
                            "Error: %s\nError URI: %s\n" % (
                                response_error.get('error_description'),
                                response_error.get('error_uri') if response_error.get('error_uri') else None)
            else:
                error_message = "Error getting 'Access token' " + \
                    "\nStatus Code: %d \nReason: %s\n" % (
                        token_response.status_code, token_response.reason) + \
                            "Error: %s\nError Message: %s\n" % (
                                error_body.get('code'), error_body.get('message'))
            raise ValidationError(error_message)


    @staticmethod
    def _refresh_access_token(refresh_token):
        # Method to refresh the access token using the refresh token

        token_url = 'https://oauth2.googleapis.com/token'
        client_id = self.env['ir.config_parameter'].sudo().get_param('google.oauth2.client_id')
        client_secret = self.env['ir.config_parameter'].sudo().get_param('google.oauth2.client_secret')

        refresh_payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        refresh_response = requests.post(token_url, data=refresh_payload)
        refresh_data = refresh_response.json()

        return refresh_data.get('access_token')

    @staticmethod
    def _get_valid_access_token(user):
        # Method to get a valid access token for the user

        current_time = datetime.now()
        if user.google_access_token_expiration and user.google_access_token_expiration > current_time:
            return user.google_access_token
        else:
            # Access token has expired, refresh it using the refresh token
            refreshed_token = self._refresh_access_token(user.google_refresh_token)
            user.write({'google_access_token': refreshed_token})
            return refreshed_token

    @staticmethod
    def get_google_api_session(user):
        # Method to get a session for making requests to Google API

        access_token = self._get_valid_access_token(user)
        session = requests.Session()
        session.headers.update({'Authorization': f'Bearer {access_token}'})
        return session
