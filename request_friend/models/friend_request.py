from odoo import models, fields, api, exceptions

class FriendRequest(models.Model):
    _name = 'friend.request'
    _description = 'Friend Request'
    _rec_name = 'from_partner_id'

    from_partner_id = fields.Many2one('res.partner', string='From', required=True, ondelete='cascade')
    to_partner_id = fields.Many2one('res.partner', string='To', required=True, ondelete='cascade')
    state = fields.Selection([
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
    ], default='sent', string='State', tracking=True)

    _sql_constraints = [
        ('unique_request', 'unique(from_partner_id, to_partner_id)', 'Friend request already exists!')
    ]

    # Fonction pour envoyer une demande (si elle n'existe pas)
    @api.model
    def send_request(self, from_partner_id, to_partner_id):
        existing = self.search([
            ('from_partner_id', '=', from_partner_id),
            ('to_partner_id', '=', to_partner_id)
        ])
        if existing:
            raise exceptions.UserError("Une demande d'ami existe déjà entre ces partenaires.")
        
        request = self.create({
            'from_partner_id': from_partner_id,
            'to_partner_id': to_partner_id,
        })
        return request

    # Fonction pour accepter une demande
    def accept_request(self):
        for record in self:
            if record.state != 'sent':
                raise exceptions.UserError("La demande ne peut pas être acceptée (état actuel : %s)." % record.state)
            record.state = 'accepted'

    # Fonction pour refuser une demande
    def refuse_request(self):
        for record in self:
            if record.state != 'sent':
                raise exceptions.UserError("La demande ne peut pas être refusée (état actuel : %s)." % record.state)
            record.state = 'refused'

class ResPartner(models.Model):
    _inherit = 'res.partner'

    friend_request_ids = fields.One2many('friend.request', 'to_partner_id', string='Friend Requests')
    sent_friend_request_ids = fields.One2many('friend.request', 'from_partner_id', string='Sent Friend Requests')
