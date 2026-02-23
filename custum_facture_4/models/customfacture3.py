import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    prescription_ids = fields.Many2many('prescription.order', string='Prescriptions',readonly=True)
    total_pharmacie_interne = fields.Float(string='Total Pharmacie Interne', default=1000.0)
    # total_pharmacie_interne = fields.Float(string='Total Pharmacie Interne', compute='_compute_total_pharmacie_interne')

    # @api.depends('prescription_ids')
    # def _compute_total_pharmacie_interne(self):
    #     for record in self:
    #         total = sum(prescription.amount_total for prescription in record.prescription_ids)
    #         record.total_pharmacie_interne = total
    #         _logger.info(f"Total Pharmacie Interne computed: {total} for record ID {record.id}")

    @api.model
    def create(self, vals):
        _logger.info(f"Creating Account Move with values: {vals}")
        record = super(AccountMove, self).create(vals)
        if 'hospitalization_id' in vals:
            hospitalization_id = vals.get('hospitalization_id')
            _logger.info(f"Hospitalization ID found: {hospitalization_id}")
            prescriptions = self.env['prescription.order'].search([('hospitalization_id', '=', hospitalization_id)])
            _logger.info(f"Prescriptions found: {prescriptions.ids}")
            record.prescription_ids = [(6, 0, prescriptions.ids)]
        
        record._create_pharmacie_interne_line()
        return record

    def write(self, vals):
        _logger.info(f"Writing to Account Move ID {self.id} with values: {vals}")
        res = super(AccountMove, self).write(vals)
        for record in self:
            if 'hospitalization_id' in vals:
                hospitalization_id = vals.get('hospitalization_id')
                _logger.info(f"Hospitalization ID found: {hospitalization_id} for record ID {record.id}")
                prescriptions = self.env['prescription.order'].search([('hospitalization_id', '=', hospitalization_id)])
                _logger.info(f"Prescriptions found: {prescriptions.ids}")
                record.prescription_ids = [(6, 0, prescriptions.ids)]
            
            record._create_pharmacie_interne_line()

        return res

    @api.onchange('hospitalization_id')
    def _onchange_hospitalization_id(self):
        if self.hospitalization_id:
            _logger.info(f"Onchange triggered for Hospitalization ID: {self.hospitalization_id.id}")
            prescriptions = self.env['prescription.order'].search([('hospitalization_id', '=', self.hospitalization_id.id)])
            self.prescription_ids = [(6, 0, prescriptions.ids)]
        else:
            _logger.info("Onchange triggered with no Hospitalization ID selected.")
            self.prescription_ids = [(5, 0, 0)]  # Clear the field if no hospitalization is selected

    def _create_pharmacie_interne_line(self):
        for record in self:
            _logger.info(f"Creating Pharmacie Interne line for Account Move ID {record.id}")
            if record.total_pharmacie_interne:
                existing_line = self.invoice_line_ids.filtered(lambda l: l.name == 'Pharmacie Interne')
                
                if existing_line:
                    _logger.info(f"Updating existing line for Pharmacie Interne on Account Move ID {record.id}")
                    existing_line.update({
                        'price_unit': record.total_pharmacie_interne,
                        'quantity': 1,
                    })
                else:
                    _logger.info(f"Creating new invoice line for Pharmacie Interne on Account Move ID {record.id}")
                    self.env['account.move.line'].create({
                        'move_id': record.id,
                        'name': 'Pharmacie Interne',
                        'quantity': 1,
                        'price_unit': record.total_pharmacie_interne,
                    })
            else:
                _logger.info(f"No total Pharmacie Interne to create a line for Account Move ID {record.id}")