from odoo import http
from odoo.http import request

class YourModuleAPI(http.Controller):

    @http.route('/api/get_fields/<string:model_name>', type='http', auth='none', methods=['GET'])
    def get_fields(self, model_name):
        env = request.env
        if model_name in env:
            model = env[model_name]
            fields = model._fields
            return list(fields.keys())
        else:
            return {'error': 'Model not found'}
