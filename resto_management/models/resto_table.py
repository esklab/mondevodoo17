from odoo import models, fields, api

class RestoTable(models.Model):
    _name = 'resto.table'
    _description = 'Tables du Restaurant'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(string='Numéro de Table', required=True)
    seats = fields.Integer(string='Nombre de Places', default=2)
    state = fields.Selection([
        ('available', 'Disponible'),
        ('occupied', 'Occupée'),
        ('reserved', 'Réservée')
    ], string='Statut', default='available')
