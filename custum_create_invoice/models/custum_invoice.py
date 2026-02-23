from odoo import models, api, fields, _
import logging
from odoo.exceptions import UserError

# Configurer le logger
_logger = logging.getLogger(__name__)

class AppointmentInvoicing(models.Model):
    _inherit = 'hms.appointment'

    def create_invoice(self):
        inv_data = self.acs_appointment_inv_data()
        product_data = self.acs_appointment_inv_product_data()
        acs_context = {'commission_partner_id':self.physician_id.partner_id.id}
        if self.pricelist_id:
            acs_context.update({'acs_pricelist_id': self.pricelist_id.id})
        invoice = self.with_context(acs_context).acs_create_invoice(partner=self.patient_id.partner_id, patient=self.patient_id, product_data=product_data, inv_data=inv_data)
        self.invoice_id = invoice.id
        self.acs_appointment_common_invoicing(invoice)
        if self.state == 'to_invoice':
            self.appointment_done()

        if self.state == 'draft' and not self._context.get('avoid_confirmation'):
            if self.invoice_id and not self.company_id.acs_check_appo_payment:
                self.appointment_confirm()

    def create_consumed_prod_invoice(self):
        if not self.consumable_line_ids:
            raise UserError(_("There is no consumed product to invoice."))

        inv_data = self.acs_appointment_inv_data()
        product_data = self.acs_appointment_inv_product_data(with_product=False)

        pricelist_context = {}
        if self.pricelist_id:
            pricelist_context = {'acs_pricelist_id': self.pricelist_id.id}
        invoice = self.with_context(pricelist_context).acs_create_invoice(partner=self.patient_id.partner_id, patient=self.patient_id, product_data=product_data, inv_data=inv_data)
        self.consumable_invoice_id = invoice.id
        self.acs_appointment_common_invoicing(invoice)
        if self.state == 'to_invoice':
            self.appointment_done()

    def action_create_invoice_with_procedure(self):
        return self.with_context(with_procedure=True).create_invoice()