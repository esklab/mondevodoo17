from odoo import fields, models, api, exceptions


class WorkflowHistory(models.Model):
    _name = 'workflow.history'
    _description = 'Historique des validations'
    _order = 'validated_on desc'

    transition_id = fields.Many2one('workflow.transition', string='Transition', required=True)
    record_id = fields.Integer(string='ID du Record', required=True)
    model_name = fields.Char(string='Modèle', required=True)
    validated_by = fields.Many2one('res.users', string='Validé par', required=True)
    old_state = fields.Char(string='État précédent', required=True)
    new_state = fields.Char(string='Nouvel État', required=True)
    validated_on = fields.Datetime(string='Date de validation', default=fields.Datetime.now, required=True)

    def name_get(self):
        result = []
        for record in self:
            name = f"Transition #{record.id}: {record.old_state} → {record.new_state}"
            result.append((record.id, name))
        return result

    def action_view_record(self):
        """Action pour voir l'enregistrement associé"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.model_name,
            'view_mode': 'form',
            'res_id': self.record_id,
            'target': 'current',
        }

