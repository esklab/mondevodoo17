from odoo import models, fields, api, _

class Student(models.Model):
    _name = 'school.student'
    _description = 'Student'

    name = fields.Char(string='Name', required=True)
    birth_date = fields.Date(string='Birth Date')  # Changed from Float to Date
    note_ids = fields.One2many('school.note', 'student_id', string='Grades')  # Changed to One2many to notes

    state = fields.Selection([
        ('N', 'Normal'),
        ('H', 'Haut'),
        ('B', 'Bas'),
    ], string="State", default='N')

class Matiere(models.Model):
    _name = 'school.matiere'
    _description = 'Matiere'

    name = fields.Char(string='Name', required=True)

class Note(models.Model):
    _name = 'school.note'
    _description = 'Note'

    student_id = fields.Many2one('school.student', string='Student', required=True)  # Correct Many2one relation
    subject_id = fields.Many2one('school.matiere', string='Subject', required=True)
    score = fields.Float(string='Score', required=True)


class ReportCard(models.Model):
    _name = 'school.bulletin'
    _description = 'Report Card'

    student_id = fields.Many2one('school.student', string='Student', required=True)
    total_score = fields.Float(string='Total Score', compute='_compute_total_score', store=True)
    grade_ids = fields.One2many('school.note', 'student_id', string='Grades')  # Correct One2many relation

    @api.depends('grade_ids.score')
    def _compute_total_score(self):
        for record in self:
            record.total_score = sum(note.score for note in record.grade_ids)
