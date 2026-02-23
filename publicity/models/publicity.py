from odoo import models, fields

class Publicite(models.Model):
    _name = 'public.publicite'
    _description = 'Publicité'

    name = fields.Char(string='Nom de la publicité', required=True)
    description = fields.Text(string='Description')
    date_debut = fields.Date(string='Date de début', required=True)
    date_fin = fields.Date(string='Date de fin', required=True)
    image = fields.Binary(string='Image de la publicité')
    actif = fields.Boolean(string='Actif', default=True)
    partner_id = fields.Many2one('res.partner', string='Partenaire') 
    sponsor_id = fields.Many2one('res.partner', string='Sponsors')