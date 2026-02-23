from odoo import fields, models, api


class WorkflowState(models.Model):
    _name = 'workflow.state'
    _description = 'État du Workflow'
    _order = 'sequence, id'

    name = fields.Char(string='Nom', required=True)
    code = fields.Char(string='Code', required=True)
    workflow_id = fields.Many2one('workflow.model', string='Workflow', required=True)
    sequence = fields.Integer(string='Séquence', default=10, help="Ordre d'affichage des états")
    is_initial = fields.Boolean(string='État initial', default=False)
    is_final = fields.Boolean(string='État final', default=False)
