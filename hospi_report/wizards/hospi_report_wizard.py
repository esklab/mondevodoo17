from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError, UserError

class HospiReportWizard(models.TransientModel):
    _name = 'hospi.report.wizard'
    _description = "Rapport d'Hospitalisation"

    date_start = fields.Date(string="Date de début")
    date_end = fields.Date(string="Date de fin")
    patient_ids = fields.Many2many('hms.patient', string="Patients", domain=[('is_patient', '=', True)])
    gender = fields.Selection([
        ('male', 'Homme'),
        ('female', 'Femme'),
        ('other', 'Autre'),
    ], string="Genre")
    surgery_template_ids = fields.Many2many('hospital.surgery.template', string="Actes chirurgicaux")
    diseases_ids = fields.Many2many('hospital.diseases', string="Diagnostics")
    hospital_it_ids = fields.Many2many('hospital.it', string="Blocs opératoires")

    def _compute_age(self, birth_date):
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    def _get_patients(self):
        domain = [('is_patient', '=', True)]
        
        # Filtre par date d'hospitalisation
        if self.date_start or self.date_end:
            hosp_domain = []
            if self.date_start:
                hosp_domain.append(('admission_date', '>=', self.date_start))
            if self.date_end:
                hosp_domain.append(('admission_date', '<=', self.date_end))
            
            # Trouver les patients avec des hospitalisations correspondantes
            hosp_records = self.env['hospital.admission'].search(hosp_domain)
            patient_ids = hosp_records.mapped('patient_id').ids
            domain.append(('id', 'in', patient_ids))
        
        # Filtres supplémentaires
        if self.gender:
            domain.append(('gender', '=', self.gender))
        
        if self.surgery_template_ids:
            surgeries = self.env['hospital.surgery'].search([
                ('surgery_template_id', 'in', self.surgery_template_ids.ids)
            ])
            patient_ids = surgeries.mapped('patient_id').ids
            domain.append(('id', 'in', patient_ids))
        
        if self.diseases_ids:
            domain.append(('diseases_ids', 'in', self.diseases_ids.ids))
        
        if self.hospital_it_ids:
            surgeries = self.env['hospital.surgery'].search([
                ('hospital_it_id', 'in', self.hospital_it_ids.ids)
            ])
            patient_ids = surgeries.mapped('patient_id').ids
            domain.append(('id', 'in', patient_ids))
        
        if self.patient_ids:
            domain.append(('id', 'in', self.patient_ids.ids))
        
        return self.env['res.partner'].search(domain)

    def _get_patient_data(self, patient):
        # Calcul de l'âge
        age = self._compute_age(patient.birth_date) if patient.birth_date else 0
        
        # Genre
        gender_dict = {
            'male': 'Homme',
            'female': 'Femme',
            'other': 'Autre'
        }
        gender = gender_dict.get(patient.gender, 'Non spécifié')
        
        # Actes chirurgicaux
        surgeries = self.env['hospital.surgery'].search([
            ('patient_id', '=', patient.id)
        ])
        surgery_names = surgeries.mapped('surgery_template_id.name')
        
        # Diagnostics
        diseases = patient.diseases_ids.mapped('name')
        
        # Blocs opératoires
        operation_blocks = surgeries.mapped('hospital_it_id.name')
        
        # Hospitalisations
        hosp_domain = [('patient_id', '=', patient.id)]
        if self.date_start:
            hosp_domain.append(('admission_date', '>=', self.date_start))
        if self.date_end:
            hosp_domain.append(('admission_date', '<=', self.date_end))
        
        hospitalizations = self.env['hospital.admission'].search(hosp_domain)
        
        return {
            'name': patient.name,
            'age': age,
            'gender': gender,
            'surgeries': ', '.join(surgery_names),
            'diseases': ', '.join(diseases),
            'operation_blocks': ', '.join(operation_blocks),
            'hospitalizations': hospitalizations,
        }

    def action_generate_report(self):
        patients = self._get_patients()
        if not patients:
            raise UserError(_("Aucun patient trouvé avec les critères sélectionnés"))
        
        # Préparer les données pour le rapport
        data = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'patients': [self._get_patient_data(patient) for patient in patients],
        }
        
        return self.env.ref('hospital_report.report_hospi_report_wizard').report_action(self, data=data)