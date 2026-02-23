from odoo import _, api, fields, models, tools 
from odoo.exceptions import UserError, ValidationError
import time
from werkzeug import urls

class PaymentTransaction(models.Model):

    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'cashpay':
            return res
        api_data = self._get_api_bill_data()
        return {
            'api_url': api_data.get('bill_url'),
            'order_reference': api_data.get('order_reference'),
            'reference':self.reference,
        }

    def _get_api_bill_data(self):
        base_url = self.provider_id.get_base_url()
        salt = str(time.time())
        data = {
            'amount': int(self.amount),
            'merchant_reference': self.reference + "|" + salt,
            'description': 'Paiement dela facture N°' + self.reference,
            'callback_url': base_url + '/callback',
            'redirect_url': base_url + '/return',
            'client': {
                'lastname': self.partner_id.name,
                'firstname': self.partner_id.name,
                'phone':self.partner_id.phone if self.partner_id.phone else '+22892416645',
            },
            'direct_pay': 0,
            'gateway': 1,
            
        }
        
        response = self.provider_id._cashapy_make_request(salt, data)

        return {
            'bill_url': response.get('bill_url'),
            'order_reference': response.get('order_reference'),
            
        }
    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        """ Override of payment to find the transaction based on cashpay data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
   
        tx = super()._get_tx_from_feedback_data(provider_code, data)
        if provider_code != 'cashpay':
            return tx

        reference = data.get('reference')
        tx = self.search([('reference', '=', reference), ('code', '=', 'cashpay')])
        return tx

    def _process_feedback_data(self, data):
        """ Override of payment to process the transaction based on dummy data.

        Note: self.ensure_one()

        :param dict data: The dummy feedback data
        :return: None
        :raise: ValidationError if inconsistent data were received
        """ 
        self.ensure_one()
        super()._process_feedback_data(data)
        if self.provider_code != "cashpay":
            return
       