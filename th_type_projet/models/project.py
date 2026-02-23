from odoo import _, api, fields, models, tools 
from odoo.exceptions import UserError, ValidationError
import datetime

class TypeProjet(models.Model):

    _name = 'type.projet'
    _description = 'Type de projet'
    
    name = fields.Char(string='Nom du type')
    state_ids = fields.One2many('type.projet.line', 'type_id')

class TypeProjetLine(models.Model):

    _name = 'type.projet.line'
    _description = 'Ligne de type de projet'

    name = fields.Char(string='Nom')
    phase_id = fields.Many2one(
        'stage.type',
        string='Type de phase',
        )
    task_ids = fields.One2many('type.projet.line.task', 'line_id')
    type_id = fields.Many2one(
        'type.projet',
        string='Type de projet',
    )

class ProjectTask(models.Model):

    _inherit = 'project.task'

    date_fin = fields.Datetime(string='Date de fin de tâche')

class TypeProjetLineTask(models.Model):    
    _name = 'type.projet.line.task'
    _description = ''

    name = fields.Char(string='Nom de la tâche')
    type_dure = fields.Selection([
        ('1', 'Heure'),
        ('2', 'Jour')
    ])
    type_id = fields.Many2one(
        'task.type',
        string='Type de tâche',
        )
    nbr_jour_heure = fields.Integer(string='Nombre de jours ou heures')
    line_id = fields.Many2one(
        'type.projet.line',
        string='Ligne de tâche',
        )

class StageType(models.Model):

    _name = 'stage.type'
    _description = 'Type de phase'
    name = fields.Char(string='Nom du type')

class TaskType(models.Model):

    _name = 'task.type'
    _description = 'Type de tâche'
    name = fields.Char(string='Nom du type')

class ProjectProject(models.Model):

    _inherit = 'project.project'

    date = fields.Datetime(string='Date de début') 
    cout = fields.Float(string='Coût estimatif')

    def get_numero(self):
        numero = self.env['ir.sequence'].next_by_code(
                'project_project')
        return numero
    numero = fields.Char(string='Numéro de projet', default=get_numero)
    type_projet_id = fields.Many2one(
        'type.projet',
        string='Type Projet',
    )


    @api.model
    def create(self, vals):
        if 'date' not in vals or not vals['date']:
            raise ValidationError(_('Veuillez spécifier une date de début pour le projet.'))

        project = super(ProjectProject, self).create(vals)
        if vals.get('numero', 'Numéro') == 'Numéro':
            vals['numero'] = self.env['ir.sequence'].next_by_code(
                'project_project') or 'Numéro'

        stage_names = []
        id = vals['type_projet_id']
        lines = self.env['type.projet.line'].search([('type_id','=',id)])
        for line in lines:
            stage_names.append({
                'id':line.id,
                'name' : line.name,
                'tasks': line.task_ids
            })

        stages = self.env['project.task.type']
        created_stages = []
        for my_stage in stage_names:
            stage = stages.create({'name': my_stage['name'], 'sequence': len(stages)+1, 'project_ids': [(4, project.id)]})
            created_stages.append(stage)
            for task in my_stage['tasks']:
                if task.type_dure == 'Heure':
                    deadline = datetime.datetime.strptime(vals['date'], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=task.nbr_jour_heure)
                else:
                    deadline = datetime.datetime.strptime(vals['date'], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=task.nbr_jour_heure)

                task1 = self.env['project.task'].create({'name': task.name,'date_deadline':deadline ,'project_id': project.id, 'stage_id': stage.id})

        return project
