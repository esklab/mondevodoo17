from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
import logging
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError
import random
import json
import requests
import pytz
_logger = logging.getLogger(__name__)
TIMEOUT = 20
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

class MeetCalendarEvent(models.Model):
    _inherit = "calendar.event"

    google_link_check = fields.Boolean(string="Generate Google Meet Link",
                                      tracking=True)
    google_meeting_url = fields.Char(string="Google Meet URL")
    meet_warning_check = fields.Boolean(default=False)
    meet_eventid = fields.Char()

    @api.onchange('google_link_check')
    def _check_teams_bool(self):
        """Trigger 'worning_check' boolean if user
        tries to turn off meeting link boolean.
        """
        if self.create_uid and self.google_meeting_url:
            if not self.google_link_check:
                self.meet_warning_check = True
            elif self.google_link_check:
                self.meet_warning_check = False

    @api.model_create_multi
    def create(self, values):
        active_user = self.env.user
        for vals in values:
            if vals.get('description') and 'Google Meet' in vals.get('description'):
                user_id = vals.get('user_id')
                user = self.env['res.users'].sudo().browse(user_id)
                active_user = user
                vals['google_link_check'] = True
            if all([vals.get('google_link_check'), vals.get('recurrency')]):
                raise UserError(
                    "Google Meet Event can't create with Recurring Events..!")
            elif vals.get('google_link_check') and not vals.get('recurrency'):
                #if not active_user.is_authenticated:
                    #raise ValidationError(
                        #"Generate an access token to create a Microsoft Teams meeting.")

                attendee = self.prepare_attendee_vals(vals.get('partner_ids'))
                vals['start'] = str(vals['start'])
                vals['stop'] = str(vals['stop'])
                if vals.get('allday'):
                    start_time = datetime.strptime(
                        vals['start_date'], '%Y-%m-%d') if \
                        'start_date' in vals.keys() else self.start_date
                    end_time = datetime.strptime(
                        vals['stop_date'], '%Y-%m-%d') if \
                        'stop_date' in vals.keys() else self.stop_date
                    vals['start'] = str(start_time)
                    vals['stop'] = str(end_time + timedelta(days=1))
                else:
                    start_time = vals['start']
                    end_time = vals['stop']
                meeting_link = self.generate_google_meet_link_one(vals, attendee, active_user)
                vals['start'] = start_time
                vals['stop'] = end_time
                vals['google_meeting_url'] = meeting_link.get('meeting_url')
                vals['meet_eventid'] = meeting_link.get('meeting_id')
                vals['description'] = meeting_link.get('meeting_body')

        return super(MeetCalendarEvent, self).create(values)


    def prepare_attendee_vals(self, values):
        """
        Make a list of dictionary of participant's names and email addresses.
        """
        attendees = []
        res_partner = self.env['res.partner']
        for value in values:
            attendees.append(
                {
                    "emailAddress":
                        {
                            "address": res_partner.browse(value[1]).email,
                            "name": res_partner.browse(value[1]).name
                        },
                    "type": "required"
                }
            )
        return attendees

    def generate_google_meet_link_one(self, values, attendee, user):

        google_client_id = self.env['ir.config_parameter'].sudo().get_param('google_client_id')
        google_client_secret = self.env['ir.config_parameter'].sudo().get_param('google_client_secret')
        credentials = Credentials(
            token=user.google_access_token,
            refresh_token=user.google_refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=google_client_id,
            client_secret=google_client_secret
        )

        if credentials.expired and credentials.refresh_token:
            user.google_meet_refresh_token()
            credentials.refresh(Request())

        service = build('calendar', 'v3', credentials=credentials)



        start_date = datetime.strptime(values.get('start'), '%Y-%m-%d %H:%M:%S')
        stop_date = datetime.strptime(values.get('stop'), '%Y-%m-%d %H:%M:%S')

        _logger.info("start date before: %s", start_date)
        start = start_date.isoformat()
        end = stop_date.isoformat()

        _logger.info("start date: %s", start)

        _logger.info("the name is: %s",  values.get('name'))

        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        request_id = ''.join(
            random.SystemRandom().choice(chars) for _ in range(16))

        event = {
            'summary':  values.get('name'),
            'start': {'dateTime': start, 'timeZone': 'UTC'},
            'end': {'dateTime': end, 'timeZone': 'UTC'},
            'conferenceData': {'createRequest': {'requestId': request_id}}
        }

        event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
        _logger.info("le event finale: %s", event)
        meet_link = event.get('hangoutLink')
        if event.get('hangoutLink'):
            return {
                "meeting_body": event['conferenceData']['conferenceId'],
                "meeting_url": event['hangoutLink'],
                "meeting_id":  event['id']
            }
            #cal_event.google_event_id = result['id']
            #cal_event.google_meet_url = result['hangoutLink']
            #cal_event.google_meet_code = result['conferenceData']['conferenceId']
        else:
            raise ValidationError("Failed to create event,"
                                  "Please check your authorization connection.")

        #self.google_meet_link = meet_link

    def generate_google_meet_link(self, values,  attendees, user):
        # Charge les informations d'authentification pour l'utilisateur




        start_date = datetime.strptime(values.get('start'), '%Y-%m-%d %H:%M:%S')
        stop_date = datetime.strptime(values.get('stop'), '%Y-%m-%d %H:%M:%S')

        _logger.info("start date before: %s", start_date)
        start = start_date.isoformat()
        end = stop_date.isoformat()

        current_uid = self._context.get('uid')
        user_id = self.env['res.users'].browse(current_uid)

        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        request_id = ''.join(
            random.SystemRandom().choice(chars) for _ in range(16))
        url = 'https://www.googleapis.com/calendar/v3/calendars/primary/events?conferenceDataVersion=1&sendNotifications=True'
        header = {
            'Authorization':
                'Bearer %s' % user.google_access_token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        event = {
            'summary':  values.get('name'),

            'conferenceDataVersion': 1,
            'start': {
                'dateTime': start,
                 "timeZone": "UTC"
            },
            'end': {
                'dateTime': end,
                 "timeZone": "UTC"
            },
            'conferenceData': {
                "createRequest": {
                    'requestId': request_id
                }
            },
        }
        result = requests.post(url, headers=header, timeout=TIMEOUT,
                               data=json.dumps(event)).json()
        if result.get('error'):
            _logger.info("error here: %s", result)
            user.google_meet_refresh_token()
            result = requests.post(url, headers=header, timeout=TIMEOUT,
                                   data=json.dumps(event)).json()
        if result.get('hangoutLink'):
            return {
                "meeting_body": result['conferenceData']['conferenceId'],
                "meeting_url": result['hangoutLink'],
                "meeting_id":  result['id']
            }
            #cal_event.google_event_id = result['id']
            #cal_event.google_meet_url = result['hangoutLink']
            #cal_event.google_meet_code = result['conferenceData']['conferenceId']
        else:
            raise ValidationError("Failed to create event,"
                                  "Please check your authorization connection.")


    def action_redirect_link(self):
        """Redirects to Teams Meeting Url.
        """
        if self.google_meeting_url:
            url = self.google_meeting_url
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new'
            }