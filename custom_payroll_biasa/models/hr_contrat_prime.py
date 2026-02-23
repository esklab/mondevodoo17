# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HrContractPrime(models.Model):
    _inherit = 'hr.contract'

    PRIME_DEPLACEMENT = [
        ('2000', '2000'),
        ('3000', '3000'),
        ('7500', '7500'),
    ]
    
    PRIME_GARDE = [
        ('12500', '12500'),
        ('25000', '25000'),
    ]
    
    PRIME_SUGGESTION = [
        ('15000', '15000'),
        ('30000', '30000'),
    ]
    
    PRIME_ASTREINTE  = [
        ('10000', '10000'),
        ('15000', '15000'),
    ]
    
    PRIME_PERMANENCE = [
        ('2000', '2000'),
        ('3000', '3000'),
        ('10000', '10000'),
    ]

    montantprimedeplacement = fields.Selection(PRIME_DEPLACEMENT, string='Prime Deplacement')
    montantprimegarde = fields.Selection(PRIME_GARDE, string='Prime de Garde')
    montantprimesuggestion = fields.Selection(PRIME_SUGGESTION, string='Prime de sujetion')
    montantprimeastreinte = fields.Selection(PRIME_ASTREINTE, string='Prime astreinte')
    montantprimepermanence = fields.Selection(PRIME_PERMANENCE, string='Prime permanence')
    nombre_de_fois_deplacement = fields.Integer(string='Nombre de deplacement')
    nombre_de_fois_garde = fields.Integer(string='Nombre de garde')
    nombre_de_fois_suggestion = fields.Integer(string='Nombre de sujetion')
    nombre_de_fois_astreinte = fields.Integer(string='Nombre de astreinte')
    nombre_de_fois_permanence = fields.Integer(string='Nombre de permanence')
 
    @api.onchange('montantprimedeplacement', 'nombre_de_fois_deplacement')
    def _compute_total_prime_deplacement(self):
        for record in self:
            if record.montantprimedeplacement and record.nombre_de_fois_deplacement:
                record.x_studio_indemnit_de_dplacement = float(record.montantprimedeplacement) * record.nombre_de_fois_deplacement
            else:
                record.x_studio_indemnit_de_dplacement = record.x_studio_indemnit_de_dplacement

    @api.onchange('montantprimegarde', 'nombre_de_fois_garde')
    def _compute_total_prime_garde(self):
        for record in self:
            if record.montantprimegarde and record.nombre_de_fois_garde:
                record.prime_garde = float(record.montantprimegarde) * record.nombre_de_fois_garde
            else:
                record.prime_garde = record.prime_garde

    @api.onchange('montantprimesuggestion', 'nombre_de_fois_suggestion')
    def _compute_total_prime_suggestion(self):
        for record in self:
            if record.montantprimesuggestion and record.nombre_de_fois_suggestion:
                record.x_studio_prime_de_sujetion = float(record.montantprimesuggestion) * record.nombre_de_fois_suggestion
            else:
                record.x_studio_prime_de_sujetion = record.x_studio_prime_de_sujetion  

    @api.onchange('montantprimeastreinte', 'nombre_de_fois_astreinte')
    def _compute_total_prime_astreinte(self):
        for record in self:
            if record.montantprimeastreinte and record.nombre_de_fois_astreinte:
                record.astreinte = float(record.montantprimeastreinte) * record.nombre_de_fois_astreinte
            else:
                record.astreinte = record.astreinte

    @api.onchange('montantprimepermanence', 'nombre_de_fois_permanence')
    def _compute_total_prime_permanence(self):
        for record in self:
            if record.montantprimepermanence and record.nombre_de_fois_permanence:
                record.x_studio_prime_de_permanence = float(record.montantprimepermanence) * record.nombre_de_fois_permanence
            else:
                record.x_studio_prime_de_permanence = record.x_studio_prime_de_permanence