# -*- coding: utf-8 -*-
from odoo import models, fields

class Event(models.Model):
    _inherit = 'event.event'

    x_studio_many2one_project = fields.Many2one('project.project', string="Project", readonly=True)

class Project(models.Model):
    _inherit = 'project.project'

    x_studio_many2many_field_7hHkT = fields.Many2many('event.event', string="Events")

    def write(self, vals):
        res = super(Project, self).write(vals)
        for project in self:
            # Vérifier si des événements sont associés au projet
            if project.x_studio_many2many_field_7hHkT:
                # Mettre à jour l'ID du projet dans les événements associés
                project.x_studio_many2many_field_7hHkT.write({'x_studio_many2one_project': project.id})
        return res