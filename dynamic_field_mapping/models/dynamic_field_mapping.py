from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError


class DynamicFieldMapping(models.Model):
    _name = 'dynamic.field.mapping'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Dynamic Field Mapping"
    _rec_name = 'mapping_model_to'

    # mapping_model_from = fields.Selection(selection=[], string="Mapping Model From",
    #                                       help="Select model from which you want to mapped fields", tracking=True)
    # mapping_model_to = fields.Selection(selection=[], string="Mapping Model To",
    #                                     help="Select model in which you want to mapped fields", tracking=True)
    line_ids = fields.One2many(comodel_name='dynamic.field.mapping.line', inverse_name='dynamic_field_mapping_id',
                               string="Field Mapping Lines")

    _sql_constraints = [
        ('mapping_model_to_uniq', 'unique(mapping_model_from, mapping_model_to)', 'Mapping models must be unique!'),
    ]

    def _get_models(self):
        models = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in models]

    mapping_model_from = fields.Selection(selection=lambda self: self._get_models(), string="Mapping Model From", tracking=True)
    mapping_model_to = fields.Selection(selection=lambda self: self._get_models(), string="Mapping Model To", tracking=True)

    @api.constrains('line_ids')
    def check_field_type(self):
        for record in self:
            for line in record.line_ids:
                if not line.mapping_model_from_field_selection_id or not line.mapping_model_to_field_selection_id:
                    continue
                if line.mapping_model_from_field_selection_id.ttype != line.mapping_model_to_field_selection_id.ttype:
                    raise ValidationError("Les types de champ doivent être identiques dans le modèle source et destination.")
                if line.mapping_model_from_field_selection_id.ttype in ['many2one', 'one2many', 'many2many']:
                    if line.mapping_model_from_field_selection_id.relation != line.mapping_model_to_field_selection_id.relation:
                        raise ValidationError("Les relations des champs relationnels doivent être identiques.")
                if (line.mapping_model_from_field_selection_id.model != record.mapping_model_from or
                        line.mapping_model_to_field_selection_id.model != record.mapping_model_to):
                    raise ValidationError("Les champs doivent appartenir aux modèles sélectionnés.")
            
    def write(self, vals):
        if 'line_ids' in vals:
            old_values = ""
            for line in self.line_ids:
                old_values += f"<tr><td>{line.mapping_model_from_field_selection_id.display_name}</td>"
                old_values += f"<td>{line.mapping_model_to_field_selection_id.display_name}</td></tr>"
        
            if old_values:
                self.message_post(body=tools.html_sanitize(f"<strong>Anciennes valeurs :</strong><table>{old_values}</table>"))

        res = super(DynamicFieldMapping, self).write(vals)

        if 'line_ids' in vals:
            new_values = ""
            for line in self.line_ids:
                new_values += f"<tr><td>{line.mapping_model_from_field_selection_id.display_name}</td>"
                new_values += f"<td>{line.mapping_model_to_field_selection_id.display_name}</td></tr>"

            if new_values:
                self.message_post(body=tools.html_sanitize(f"<strong>Nouvelles valeurs :</strong><table>{new_values}</table>"))

        return res
