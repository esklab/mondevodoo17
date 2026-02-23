from odoo import models, fields

class RecForm(models.Model):
    _name = 'rec.form'

    name = fields.Char(string='Nom')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    message = fields.Text(string='Message')