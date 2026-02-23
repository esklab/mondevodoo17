import logging
import re
from datetime import datetime, timedelta
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class RdvConsultationCalendarEvent(models.Model):

    _inherit = "calendar.event"

    @api.model_create_multi
    def create(self, values):
        employee = ""
        active_user = ""
        nom_complet = "",
        telephone = "",
        email = "",
        code_patient = "",
        event_date = "",
        for vals in values:
            user_id = vals.get('user_id')
            event_date = vals.get('start_date')
            try:
                user = self.env['res.users'].sudo().browse(user_id)
            except Exception as e:
                exception_message = str(e)
                raise UserError("Une erreur s'est produite lors de la création : %s" % exception_message)
            _logger.info("le user est: %s", user)
            employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
            _logger.info("le active employee: %s", employee)
            if employee:
                active_user = self.env['hms.physician'].search([('employee_id', '=', employee.id)], limit=1)
                if not active_user:
                    raise UserError(
                        "Cet utilisateur n'est pas liee au model Medecin")
            else:
                raise UserError(
                    "Cet utilisateur n'est pas liee au model employee")
            code_patient = self.search_code_element(vals.get('description'))
            nom_complet = vals.get('name').split(" - ", 1)
            telephone = re.search(r'Téléphone : ([\+\d]+)', vals.get('description'))
            email = re.search(r'Email : ([\w\.-]+@[\w\.-]+)', vals.get('description'))
            _logger.info("nom sans filtre: %s", vals.get('name'))

        _logger.info("le code est: %s", code_patient)

        _logger.info("le active user: %s", active_user)
        patient_id = self.check_and_create_hms_patient(nom_complet[0], telephone, email , code_patient)
        #values['patient_id'] = patient_id


        _logger.info("nom complet value: %s", nom_complet)
        _logger.info("Creating record with values: %s", values)
        appointment = super(RdvConsultationCalendarEvent, self).create(values)
        self.create_hms_appointment(event_date, patient_id, active_user)
        return appointment

    def search_code_element(self, string):
        resultat = re.search(r'code patient: (\w+)', string)

        # Vérifier si le code patient est trouvé
        if resultat:
            # Extraire le code patient
            code_patient = resultat.group(1)
            return code_patient
        else:
           return ""

    def check_and_create_hms_patient(self, name, telephone, email, code):
        # Vérifier si le patient existe dans HMS
        _logger.info("start search")
        patient = self.env['hms.patient'].search([('code', '=', code)], limit=1)
        _logger.info("le patient trouver: %s", patient)
        if not patient:
            # Création du patient s'il n'existe pas
            patient = self.env['hms.patient'].create({
                'name': name
                # Ajoutez d'autres champs requis pour la création du patient dans HMS
            })
        return patient.id

    def create_hms_appointment(self, event_date, patient_id, active_user):
        # Récupération des données du rendez-vous
        hms_appointment_vals = {
            'patient_id': patient_id,
            'physician_id': active_user.id,
            'date': event_date,
            # Ajoutez d'autres champs requis pour la création du rendez-vous dans HMS
        }
        # Création du rendez-vous dans le module HMS
        self.env['hms.appointment'].create(hms_appointment_vals)