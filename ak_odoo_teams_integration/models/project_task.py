from odoo import models, fields, api
import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'
    @api.model
    def create(self, vals):
        task = super(ProjectTask, self).create(vals)
        _logger.info("Tâche créée : %s", task.name)
        end_date = task.date_deadline + timedelta(days=1)
        # Créer un événement dans le module Agenda
        event = self.env['calendar.event'].create({
            'name': task.name,
            'start': task.date_deadline,  # Utilisez la date de la ligne de date de la tâche
            'stop': end_date,
            # Autres champs de l'événement que vous souhaitez définir
        })
        _logger.info("Evénement créé : %s", event.name)
        return task