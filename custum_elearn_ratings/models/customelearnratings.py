# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    @api.onchange('x_studio_course_rating')
    def _onchange_course_rating(self):
        if self.x_studio_course_rating and self.channel_id:
            # Recalculer la moyenne du cours
            self.channel_id._compute_average_rating()
            
            return {
                'warning': {
                    'title': "Rating Changed",
                    'message': f"You have rated the course with {self.x_studio_course_rating} stars.",
                }
            }

class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    x_average_rating = fields.Float(
        string='Average Rating',
        compute='_compute_x_average_rating',
        store=True,
        readonly=True
    )

    def _compute_x_average_rating(self):
        for channel in self:
            total_rating = 0
            rated_partners = 0
            for partner in channel.channel_partner_ids:
                if partner.x_studio_course_rating:
                    total_rating += int(partner.x_studio_course_rating)
                    rated_partners += 1
            channel.x_average_rating = total_rating / rated_partners if rated_partners else 0
