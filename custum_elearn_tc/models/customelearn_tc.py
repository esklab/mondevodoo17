from odoo import models, fields,api

class ParticipantSkill(models.Model):
    _name = 'partner.skill'
    _description = 'Participant Skill'

    partner_id = fields.Many2one('slide.channel.partner', string='Participant', required=True)
    skill_id = fields.Many2one('x_skills', string='Competences', required=True, domain="[('id', 'in', x_studio_competences)]")
    validated = fields.Boolean(string='Acquis', default=False)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            return {'domain': {'skill_id': [('id', 'in', self.partner_id.x_studio_competences.ids)]}}
        else:
            return {'domain': {'skill_id': [('id', 'in', [])]}}

class Participant(models.Model):
    _inherit = 'slide.channel.partner'

    participant_skill_ids = fields.One2many('partner.skill', 'partner_id', string='Competences du participant')

    @api.model
    def create(self, vals):
        res = super(Participant, self).create(vals)
        for skill in res.x_studio_competences:
            self.env['partner.skill'].create({
                'partner_id': res.id,
                'skill_id': skill.id,
            })
        return res


"""from odoo import models, fields, api

class Participant(models.Model):
    _inherit = 'slide.channel.partner'

    formation_skill_ids = fields.Many2many('x_skills', string='Skills', related='channel_id.x_studio_many2many_field_dzOcK')
    acquired_skill_ids = fields.One2many('partner.skill.rel', 'partner_id', string='Acquired Skills')

    @api.depends('channel_id.x_studio_many2many_field_dzOcK')
    def _compute_formation_skills(self):
        for participant in self:
            if participant.channel_id:
                participant.formation_skill_ids = participant.channel_id.x_studio_many2many_field_dzOcK

    @api.depends('acquired_skill_ids.acquired')
    def _compute_acquired_skills(self):
        for participant in self:
            acquired_skills = self.env['partner.skill.rel'].search([('partner_id', '=', participant.id), ('acquired', '=', True)])
            participant.skill_acquired_ids = acquired_skills.mapped('skill_id')

    skill_acquired_ids = fields.Many2many('x_skills', string='Acquired Skills', compute='_compute_acquired_skills', store=True)

    @api.depends('skill_acquired_ids')
    def _compute_note(self):
        for participant in self:
            participant.note = len(participant.skill_acquired_ids)

    note = fields.Integer(string='Note', compute='_compute_note', store=True)

    @api.model
    def create(self, vals):
        res = super(Participant, self).create(vals)
        if res.formation_skill_ids:
            for skill in res.formation_skill_ids:
                self.env['partner.skill.rel'].create({
                    'partner_id': res.id,
                    'skill_id': skill.id,
                })
        return res
    
    def write(self, vals):
        res = super(Participant, self).write(vals)
        if 'formation_skill_ids' in vals:
            for participant in self:
                participant._update_participant_skills()
        return res

    def _update_participant_skills(self):
        self.ensure_one()
        if self.channel_id:
            self.formation_skill_ids = self.channel_id.x_studio_many2many_field_dzOcK

class ParticipantSkillRel(models.Model):
    _name = 'partner.skill.rel'
    _description = 'Participant Skill Rel'

    partner_id = fields.Many2one('slide.channel.partner', string='Participant', required=True)
    skill_id = fields.Many2one('x_skills', string='Skill', required=True)
    acquired = fields.Boolean(string='Acquired', default=False)
"""