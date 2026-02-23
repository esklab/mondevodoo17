from odoo import fields, models, api

class DynamicFieldMappingLine(models.Model):
    _name = 'dynamic.field.mapping.line'
    _description = "Dynamic Field Mapping Line"

    dynamic_field_mapping_id = fields.Many2one(comodel_name='dynamic.field.mapping')
    mapping_model_from_field_selection_id = fields.Many2one(comodel_name='ir.model.fields')
    mapping_model_to_field_selection_id = fields.Many2one(comodel_name='ir.model.fields')

    @api.onchange('mapping_model_to_field_selection_id', 'mapping_model_from_field_selection_id')
    def _onchange_mapping_model(self):
        if self.dynamic_field_mapping_id:
            return {
                'domain': {
                    'mapping_model_from_field_selection_id': [('model', '=', self.dynamic_field_mapping_id.mapping_model_from)],
                    'mapping_model_to_field_selection_id': [('model', '=', self.dynamic_field_mapping_id.mapping_model_to)]
                }
            }
