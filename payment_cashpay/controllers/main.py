from odoo import _, http, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.http import request, Response
from ..lib import jwt
import json
import os

class CashpayController(http.Controller):
    @http.route('/callback/',csrf=False, methods=['POST'], type="json", auth='public')
    def cashpay_callback_from_redirect(self, **call_kw):

        cashpay_api = request.env['payment.provider'].sudo().search([('code','=','cashpay')], limit=1)
        _data = json.loads(request.httprequest.data)

        token = _data['token']

        data = jwt.decode(token, cashpay_api.cashpay_api_key, algorithms=["HS256"])

        state = data['state']

        transacton_ref = data['merchant_reference'].split('|')[0]
        transaction = request.env['payment.transaction'].sudo().search([('reference','=',transacton_ref)], limit=1)

        if state == 'Paid':
            transaction._set_done()
            transaction._cron_finalize_post_processing()
        if state == 'Error':
            # transaction._cron_finalize_post_processing()
            transaction._set_error('Erreur lors du paiement de la facture N°' + transacton_ref)
        if state == 'Pending':
            transaction._set_pending()

        return Response(transacton_ref)
    
    @http.route('/return', website=True, type="http", auth='public')
    def cashpay_return_from_redirect(self, **call_kw):
        return request.redirect('/my')
