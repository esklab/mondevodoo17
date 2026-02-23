from odoo import http
from odoo.http import request

class RoomBookingController(http.Controller):

    @http.route('/room/booking', type='http', auth='public', website=True)
    def room_booking_form(self, **kwargs):
        rooms = request.env['hotel.room'].search([('is_room_avail', '=', True)])
        return request.render('hotel_management_odoo.room_booking_template', {'rooms': rooms})

    @http.route('/room/booking/submit', type='http', auth='public', website=True, csrf=True)
    def submit_room_booking(self, **post):
        partner = request.env['res.partner'].sudo().create({
            'name': post.get('name'),
            'email': post.get('email'),
            'phone': post.get('phone'),
        })
        booking = request.env['room.booking'].sudo().create({
            'partner_id': partner.id,
            'checkin_date': post.get('checkin_date'),
            'checkout_date': post.get('checkout_date'),
        })
        room_ids = post.getlist('room_ids')
        for room_id in room_ids:
            request.env['room.booking.line'].sudo().create({
                'booking_id': booking.id,
                'room_id': int(room_id),
                # Ajoutez d'autres champs nécessaires ici
            })
        return request.redirect('/thank-you')
