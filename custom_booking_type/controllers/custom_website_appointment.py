from odoo import http
from odoo.http import request

class WebsiteAppointment(http.Controller):

    @http.route('/custom/appointment/form', type='http', auth="public", website=True)
    def custom_appointment_form(self, **kwargs):
        appointment_types = request.env['appointment.type'].sudo().search([])
        return request.render("custom_booking_type.custom_appointment_form_template", {
            'appointment_types': appointment_types
        })

    @http.route('/custom/appointment/submit', type='http', auth="public", methods=['POST'], website=True)
    def custom_appointment_submit(self, **post):
        appointment_type_id = int(post.get('appointment_type_id'))
        slot_id = int(post.get('slot_id'))
        resource_id = int(post.get('resource_id'))
        
        # Créer un enregistrement d'un rendez-vous (exemple)
        request.env['appointment'].sudo().create({
            'appointment_type_id': appointment_type_id,
            'slot_id': slot_id,
            'resource_id': resource_id,
        })
        
        return request.redirect('/custom/appointment/form?success=1')

    @http.route('/appointment/get_slots', type='json', auth="public")
    def get_slots(self, appointment_type_id):
        slots = request.env['appointment.slot'].sudo().search([('appointment_type_id', '=', int(appointment_type_id))])
        return [{
            'id': slot.id,
            'name': slot.name,
            'resource_id': {'id': slot.resource_id.id, 'name': slot.resource_id.name} if slot.resource_id else {}
        } for slot in slots]