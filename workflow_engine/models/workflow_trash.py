from odoo import fields, models, api, exceptions


class WorkflowTrash(models.Model):
    _name = 'workflow.trash'
    _description = 'Corbeille des validations'
    _order = 'create_date desc'

    name = fields.Char(string='Nom')
    model_name = fields.Char(string='Modèle')
    record_id = fields.Integer(string='ID du Record')
    state = fields.Char(string='État actuel')
    requested_by = fields.Many2one('res.users', string='Requérant')
    transition_id = fields.Many2one('workflow.transition', string='Transition')
    create_date = fields.Datetime(string='Date de création', readonly=True)

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} ({record.create_date.strftime('%d/%m/%Y %H:%M') if record.create_date else 'N/A'})"
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

