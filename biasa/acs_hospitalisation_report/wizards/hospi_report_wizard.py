from odoo import models, fields, api
from datetime import datetime

class HospitalisationAnnualReportWizard(models.TransientModel):
    _name = 'acs.hospitalisation.annual.report.wizard'
    _description = 'Wizard pour le rapport annuel d\'hospitalisation'

    year = fields.Integer(string="Année", required=True, default=lambda self: fields.Date.today().year)
    gender = fields.Selection([
        ('male', 'Homme'),
        ('female', 'Femme'),
        ('other', 'Autre'),
    ], string="Genre")

    def print_report(self):
        monthly_data = {
            'entries': [self.get_month_data(m, self.year) for m in range(1, 13)],
            'discharges': [self.get_discharge_month_data(m, self.year) for m in range(1, 13)],
            'discharged_patients': [self.get_discharged_state_month_data(m, self.year) for m in range(1, 13)],
            'gender_data': [self.get_gender_month_data(m, self.year) for m in range(1, 13)],
            'months': ['JANVIER', 'FEVRIER', 'MARS', 'AVRIL', 'MAI', 'JUIN',
                      'JUILLET', 'AOUT', 'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DECEMBRE']
        }

        data = {
            'year': self.year,
            'selected_gender': dict(self._fields['gender'].selection).get(self.gender) if self.gender else 'Tous',
            'monthly_data': monthly_data,
        }

        return self.env.ref('acs_hospitalisation_report.action_report_hospitalisation_annual').report_action(self, data=data)

    def _get_base_domain(self, month_start, month_end):
        domain = [
            ('hospitalization_date', '>=', month_start.strftime('%Y-%m-%d')),
            ('hospitalization_date', '<', month_end.strftime('%Y-%m-%d'))
        ]
        if self.gender:
            domain.append(('patient_id.gender', '=', self.gender))
        return domain

    def get_month_data(self, month_num, year):
        """Retourne le nombre d'admissions par mois"""
        month_start = datetime(year, month_num, 1)
        month_end = datetime(year, month_num + 1, 1) if month_num < 12 else datetime(year, 12, 31)
        return self.env['acs.hospitalization'].search_count(self._get_base_domain(month_start, month_end))

    def get_discharge_month_data(self, month_num, year):
        """Retourne le nombre de sorties par mois (basé sur discharge_date)"""
        month_start = datetime(year, month_num, 1)
        month_end = datetime(year, month_num + 1, 1) if month_num < 12 else datetime(year, 12, 31)
        domain = [
            ('discharge_date', '>=', month_start.strftime('%Y-%m-%d')),
            ('discharge_date', '<', month_end.strftime('%Y-%m-%d'))
        ]
        if self.gender:
            domain.append(('patient_id.gender', '=', self.gender))
        return self.env['acs.hospitalization'].search_count(domain)

    def get_discharged_state_month_data(self, month_num, year):
        """Retourne le nombre de patients avec state='discharge' par mois"""
        month_start = datetime(year, month_num, 1)
        month_end = datetime(year, month_num + 1, 1) if month_num < 12 else datetime(year, 12, 31)
        domain = [
            ('state', '=', 'discharge'),
            ('hospitalization_date', '>=', month_start.strftime('%Y-%m-%d')),
            ('hospitalization_date', '<', month_end.strftime('%Y-%m-%d'))
        ]
        if self.gender:
            domain.append(('patient_id.gender', '=', self.gender))
        return self.env['acs.hospitalization'].search_count(domain)

    def get_gender_month_data(self, month_num, year):
        """Retourne la répartition par genre pour un mois"""
        month_start = datetime(year, month_num, 1)
        month_end = datetime(year, month_num + 1, 1) if month_num < 12 else datetime(year, 12, 31)
        
        domain = [
            ('hospitalization_date', '>=', month_start.strftime('%Y-%m-%d')),
            ('hospitalization_date', '<', month_end.strftime('%Y-%m-%d'))
        ]
        
        hospitalizations = self.env['acs.hospitalization'].search(domain)
        
        gender_data = {
            'male': 0,
            'female': 0,
            'other': 0,
            'total': len(hospitalizations)
        }
        
        for hosp in hospitalizations:
            gender = hosp.patient_id.gender
            if gender in gender_data:
                gender_data[gender] += 1
                
        return gender_data