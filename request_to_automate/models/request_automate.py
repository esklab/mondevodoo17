import requests
from requests.auth import HTTPBasicAuth
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class LaboratoryRequest(models.Model):
    _inherit = 'acs.laboratory.request'

    def send_request_to_api(self):
        try:
            # Préparer les données dans le format attendu par l'API
            date_requested = self.date_requested or fields.Datetime.now()
            date_demande = date_requested.date() if date_requested else fields.Date.today()
            heure_demande = date_requested.time().strftime("%H:%M") if date_requested else "00:00"
            
            data = {
                "codedemande": self.x_studio_code_demande or self.name or "",
                "datedemande": date_demande.strftime("%Y-%m-%d"),
                "heuredemande": heure_demande,
                "numerohospitalisation": self.x_studio_numero_hospitalisation or "",
                "chambre": self.x_studio_chambre or "",
                "codemedecin": self.x_studio_code_medecin or "",
                "medecinprescsipteur": self.x_studio_medecin_prescripteur or "",
                "observation": self.note or None,
                "nompatient": self.patient_id.lastname or "",
                "prenompatient": self.patient_id.firstname or self.patient_id.name or "",
                "datenais": self.patient_id.birthday.strftime("%Y-%m-%d") if self.patient_id.birthday else "",
                "sexe": self._get_gender_label(),
                "telephone": self.patient_id.mobile or self.patient_id.phone or "",
                "adressepatient": self._get_patient_address(),
                "details": self._get_test_details()
            }

            # URL et authentification
            url = "https://biasa.steros.net/api/DemandeAnalyse/Synchronize"
            auth = HTTPBasicAuth('SIL_BIASA', '+V4wVA0smOE|Z#Qlamuh')

            # Envoyer les données avec une requête POST
            _logger.info(f"Envoi des données à {url} : {data}")
            response = requests.post(url, json=data, auth=auth)

            # Vérifier la réponse
            response.raise_for_status()
            _logger.info(f"Réponse de l'API : {response.json()}")
            
            # Marquer la demande comme envoyée si nécessaire
            self.write({'x_studio_envoye_a_lapi': True, 'x_studio_date_envoi': fields.Datetime.now()})
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"Erreur de connexion à l'API : {str(e)}")
            raise UserError(f"Erreur de connexion à l'API : {str(e)}")
        except Exception as e:
            _logger.error(f"Erreur inattendue : {str(e)}")
            raise UserError(f"Erreur : {str(e)}")

        return True

    def _get_gender_label(self):
        """Convertit le sexe Odoo en format attendu par l'API"""
        gender_mapping = {
            'male': 'Masculin',
            'female': 'Feminin',
            'other': 'Autre'
        }
        return gender_mapping.get(self.patient_id.gender, '')

    def _get_patient_address(self):
        """Construit l'adresse complète du patient"""
        if not self.patient_id:
            return ""
        
        address = []
        if self.patient_id.street:
            address.append(self.patient_id.street)
        if self.patient_id.street2:
            address.append(self.patient_id.street2)
        if self.patient_id.city:
            address.append(self.patient_id.city)
        if self.patient_id.zip:
            address.append(self.patient_id.zip)
        if self.patient_id.country_id:
            address.append(self.patient_id.country_id.name)
            
        return ", ".join(address) if address else ""

    def _get_test_details(self):
        """Récupère les détails des tests/examens"""
        details = []
        for sample in self.sample_ids:
            for test in sample.test_ids:
                details.append({
                    "codexam": test.x_studio_code_examen or test.code or "",
                    "libelleanalyse": test.name or "",
                    "prix": test.list_price or 0.0
                })
        return details