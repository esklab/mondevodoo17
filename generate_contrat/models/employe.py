from odoo import models, fields, api

class Employe(models.Model):
    _name = 'module.employe'
    _description = 'Informations sur l\'employé'

    nom = fields.Char(string='Nom')
    prenom = fields.Char(string='Prénom')
    poste = fields.Char(string='Poste')
    salaire = fields.Float(string='Salaire')

    def generate_report(self):
        # Logique de génération du rapport
        data = {
            'doc_ids': self.ids,
            'doc_model': 'module.employe',
            'docs': self,
        }
        return self.env.ref('module.report_employe').report_action(self, data=data)
