# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import uuid
import logging
_logger = logging.getLogger(__name__)

class LaboratoryRequest(models.Model):
    _inherit = 'acs.laboratory.request'

    def create_invoice(self):
        if not self.line_ids:
            raise UserError(_("Please add lab Tests first."))

        product_data = self.get_laboratory_invoice_data()
        acs_context = {}
        if self.pricelist_id:
            acs_context.update({'acs_pricelist_id': self.pricelist_id.id})
        if self.physician_id:
            acs_context.update({'commission_partner_ids':self.physician_id.partner_id.id})

        invoice = self.with_context(acs_context).acs_create_invoice(partner=self.patient_id.partner_id, patient=self.patient_id, product_data=product_data, inv_data={'hospital_invoice_type': 'laboratory','physician_id': self.physician_id and self.physician_id.id or False})
        self.invoice_id = invoice.id
        invoice.request_id = self.id
        if self.state == 'to_invoice':
            self.state = 'done'

    def button_in_progress(self):
        self.state = 'in_progress'
        LabTest = self.env['patient.laboratory.test']
        Consumable = self.env['hms.consumable.line']
        gender = self.patient_id.gender

        # Liste des patients (patient principal + groupe)
        patients = self.mapped('patient_id') + self.mapped('group_patient_ids')

        for line in self.line_ids:
            for patient in patients:
                lab_test_data = self.prepare_test_result_data(line, patient)
                test_result = LabTest.create(lab_test_data)
                line.patient_lab_ids = [(4, test_result.id)]

                # Suppression de la partie critearea_ids
                # Aucun traitement lié à lab.test.critearea ne sera effectué ici

                # Création des lignes de consommables uniquement
                for con_line in line.test_id.consumable_line_ids:
                    Consumable.create({
                        'patient_lab_test_id': test_result.id,
                        'name': con_line.name,
                        'product_id': con_line.product_id.id if con_line.product_id else False,
                        'product_uom_id': con_line.product_uom_id.id if con_line.product_uom_id else False,
                        'qty': con_line.qty,
                        'date': fields.Date.today(),
                    })

    def prepare_sample_data(self, line, patient):
        return {
            'sample_type_id': line.test_id.sample_type_id.id if line.test_id.sample_type_id else False,
            'request_id': line.request_id.id if line.request_id else False,
            'user_id': self.env.user.id,
            'patient_id': patient.id,
            'company_id': line.request_id.sudo().company_id.id if line.request_id else False,
            'test_ids': [(4, line.test_id.id)] if line.test_id else [],
        }

    def create_sample(self):
        Sample = self.env['acs.patient.laboratory.sample']
        patients = self.mapped('patient_id') + self.mapped('group_patient_ids')

        for line in self.line_ids:
            if line.test_id.sample_type_id:
                # Vérifier si un échantillon existe déjà
                sample_exist = Sample.search([
                    ('request_id', '=', line.request_id.id),
                    ('sample_type_id', '=', line.test_id.sample_type_id.id)
                ])

                if not sample_exist:
                    # Créer un nouvel échantillon pour chaque patient
                    for patient in patients:
                        lab_sample_data = self.prepare_sample_data(line, patient)
                        Sample.create(lab_sample_data)
                elif not line.test_id.acs_use_other_test_sample:
                    # Si un échantillon existe mais ne peut pas être réutilisé
                    for patient in patients:
                        lab_sample_data = self.prepare_sample_data(line, patient)
                        Sample.create(lab_sample_data)
                else:
                    # Ajouter les tests au sample existant
                    sample_exist.test_ids = [(4, line.test_id.id)]