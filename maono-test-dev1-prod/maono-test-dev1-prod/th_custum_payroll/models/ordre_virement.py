from odoo import _, api, fields, models, tools 
from odoo.exceptions import UserError, ValidationError

class HrVirement(models.Model):

    _name = 'hr.virement'
    _description = 'Ordre de virement bancaire'

    name = fields.Char(string='Référence')
    date = fields.Date(string='Date')
    payslip_ids = fields.Many2many('hr.payslip')
    check_number = fields.Char(string="Numéro de chèque")
    bank_id = fields.Many2one(
      'res.bank',
      string='Banque',
    )
    mois_de_paie = fields.Selection([
      ('Janvier','Janvier'),
      ('Février','Février'),
      ('Mars','Mars'),
      ('Avril','Avril'),
      ('Mai','Mai'),
      ('Juin','Juin'),
      ('Juillet','Juillet'),
      ('Août','Août'),
      ('Septembre','Septembre'),
      ('Octobre','Octobre'),
      ('Novembre','Novembre'),
      ('Décembre','Décembre'),
    ])

    annee = fields.Integer(string="Année")