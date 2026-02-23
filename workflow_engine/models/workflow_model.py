from odoo import models, fields, api, exceptions


class WorkflowModel(models.Model):
    _name = 'workflow.model'
    _description = 'Modèle de Workflow'

    name = fields.Char(string='Nom', required=True)
    model_id = fields.Many2one('ir.model', string='Modèle concerné', required=True, ondelete='cascade')
    state_field = fields.Char(string='Champ État', required=True, default='state')
    states = fields.One2many('workflow.state', 'workflow_id', string='États')
    transitions = fields.One2many('workflow.transition', 'workflow_id', string='Transitions')


class WorkflowMixin(models.AbstractModel):
    """Mixin pour ajouter facilement les fonctionnalités de workflow aux modèles"""
    _name = 'workflow.mixin'
    _description = 'Mixin de Workflow'

    def get_available_transitions(self):
        """Retourne les transitions disponibles pour l'enregistrement actuel"""
        self.ensure_one()

        # Trouver le workflow pour ce modèle
        workflow = self.env['workflow.model'].search([
            ('model_id.model', '=', self._name)
        ], limit=1)

        if not workflow:
            return self.env['workflow.transition']

        current_state = self[workflow.state_field]

        # Trouver les transitions possibles
        transitions = self.env['workflow.transition'].search([
            ('workflow_id', '=', workflow.id),
            ('from_state.code', '=', current_state)
        ])

        # Filtrer par droits d'accès
        user_groups_ids = self.env.user.groups_id.ids
        available_transitions = self.env['workflow.transition']

        for transition in transitions:
            if not transition.allowed_groups or any(group.id in user_groups_ids for group in transition.allowed_groups):
                if transition._check_condition(self):
                    available_transitions += transition

        return available_transitions

    def apply_workflow_transition(self, transition_id):
        """Applique une transition de workflow spécifique"""
        self.ensure_one()
        transition = self.env['workflow.transition'].browse(transition_id)
        return transition.apply_transition(self)