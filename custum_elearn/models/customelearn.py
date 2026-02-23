# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CustomCoursSession(models.Model):
    _inherit = 'cours.session'
    
    start_time = fields.Char(string='Heure de Debut', required=True)
    end_time = fields.Char(string='Heure de Fin', required=True)

    days_of_week = fields.Many2many('my.schedule.day', string='Jours de semaine')

class ScheduleDay(models.Model):
    _name = 'my.schedule.day'

    name = fields.Char(string='Jours', required=True, translate=True)


class CustomSlideChannel(models.Model):
    _inherit = 'slide.channel'

    session_id= fields.Many2many('cours.session', string='Sessions')