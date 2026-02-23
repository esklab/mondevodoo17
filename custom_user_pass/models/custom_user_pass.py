from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResUsers(models.Model):
    _inherit = 'res.users'

    new_password = fields.Char(string="Nouveau mot de passe", password=True)
    date_exp = fields.Date(string="Date d'expriration")

    @api.model
    def create(self, vals):
        user = super(ResUsers, self).create(vals)
        if vals.get('new_password'):
            user._change_password_through_wizard(vals['new_password'])
        return user

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        if vals.get('new_password'):
            for user in self:
                user._change_password_through_wizard(vals['new_password'])
        return res

    def _change_password_through_wizard(self, password):
        self.ensure_one()
        
        # CrÃ©ation du wizard parent avec l'utilisateur
        wizard = self.env['change.password.wizard'].create({
            'user_ids': [(0, 0, {
                'user_id': self.id,
                'new_passwd': password
            })]
        })
        
        # Appel de la bonne mÃ©thode
        wizard.change_password_button()
        
        # Nettoyage du champ temporaire
        self.new_password = False