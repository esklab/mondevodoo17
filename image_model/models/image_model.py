# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ImageModel(models.Model):
    name = 'image.model'
    
    name = fields.Char(string='Name')
    image_binary = fields.Binary(string='Image')