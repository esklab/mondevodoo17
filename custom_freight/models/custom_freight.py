import logging
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError
from random import choice
from string import digits
from json import dumps
import json

_logger = logging.getLogger(__name__)

class FreightOperation(models.Model):
    _inherit = 'freight.operation'

    datetime = fields.Datetime("Date prévue")
    insurance_transport = fields.Boolean('Assurance transport')
    insurance_policy = fields.Char('N° Police d’Assurance')
    delivery_mode = fields.Selection(selection=[('port_port', 'Port à Port'), ('port_door', 'Port à Domicile')],string="Mode de livraison")
    rejection_reason = fields.Text(string="Motif de rejet")
    approval_request_date = fields.Datetime(string="Date de demande")
    approver_id = fields.Many2one('res.users', string="Approuvé par")

    are_required_fields_filled = fields.Boolean(
        string="Champs requis remplis",
        compute='_compute_required_fields',
        store=False
    )

    missing_fields = fields.Text(
        string="Champs manquants",
        compute='_compute_required_fields',
        store=False
    )

    project_id = fields.Many2one('project.project', string="Projet associé")
    task_ids = fields.One2many('project.task', 'project_id', string="Tâches du projet", related='project_id.task_ids')
    pending_task_count = fields.Integer(
        compute='_compute_pending_tasks', 
        string="Tâches en attente",
        help="Nombre de tâches non terminées"
    )

    company_id = fields.Many2one(
        'res.company', 
        string='Société', 
        default=lambda self: self.env.company,
        required=True
    )

    @api.depends('direction', 'transport', 'shipper_id', 'consignee_id', 
                'ocean_shipment_type', 'shipping_line_id', 'airline_id', 'trucker_id')
    def _compute_required_fields(self):
        field_requirements = {
            'all': ['direction', 'transport', 'shipper_id', 'consignee_id'],
            'ocean': ['ocean_shipment_type', 'shipping_line_id'],
            'air': ['airline_id'],
            'land': ['trucker_id']
        }
        field_labels = {
            'direction': "Type d'opération",
            'transport': "Mode de transport",
            'shipper_id': "Expéditeur",
            'consignee_id': "Destinataire",
            'ocean_shipment_type': "Type de transport maritime",
            'shipping_line_id': "Compagnie maritime",
            'airline_id': "Compagnie aérienne",
            'trucker_id': "Transporteur routier",
        }
        for record in self:
            missing = []
            for field in field_requirements['all'] + field_requirements.get(record.transport, []):
                if not record[field]:
                    missing.append(field_labels.get(field, field))
            record.missing_fields = "\n".join(f"- {item}" for item in missing) if missing else ""
            record.are_required_fields_filled = not bool(missing)

    @api.constrains('insurance_transport', 'insurance_policy')
    def _check_insurance(self):
        for rec in self:
            if rec.insurance_transport and not rec.insurance_policy:
                raise ValidationError("Le numéro de police est obligatoire lorsque l'assurance est activée !")

    def action_request_approval(self):
        self.ensure_one()

        # Mise à jour de l'étape et date
        waiting_approval_stage = self.env.ref('custom_freight.stage_waiting_approval')
        self.write({
            'stage_id': waiting_approval_stage.id,
            'approval_request_date': fields.Datetime.now()
        })

        # Recherche des validateurs
        group_id = self.env.ref('custom_freight.group_freight_approver').id
        approvers = self.env['res.users'].search([('groups_id', 'in', [group_id])])
        partner_ids = [user.partner_id.id for user in approvers if user.partner_id.email]

        if not partner_ids:
            raise UserError("Aucun email valide trouvé pour les validateurs.")

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_composition_mode': 'comment',
                'default_model': 'freight.operation',
                'default_res_ids': [int(self.id)],
                'default_partner_ids': [(6, 0, partner_ids)],
                'default_subject': f"Approbation requise - Dossier {self.name}",
                'default_body': (
                    "<div style='font-family: Arial, sans-serif;'>"
                    "<p>Bonjour,</p>"
                    f"<p>Le dossier <strong>{self.name}</strong> nécessite votre approbation.</p>"
                    "<p>Merci de traiter cette demande dès que possible.</p>"
                    "<p>Cordialement,</p>"
                    "<p>L'équipe logistique</p>"
                    "</div>"
                ),
            }
        }

    def action_approve(self):
        self.ensure_one()

        approved_stage = self.env.ref('custom_freight.stage_approved')
        self.write({
            'stage_id': approved_stage.id,
            'approver_id': self.env.user.id,
            'rejection_reason': False
        })

        # Rechercher les responsables logistique (par exemple)
        group_logistics = self.env.ref('custom_freight.group_freight_approver')
        users = self.env['res.users'].search([('groups_id', 'in', [group_logistics.id])])
        partner_ids = [user.partner_id.id for user in users if user.partner_id]
    
        # Abonner automatiquement
        if partner_ids:
            self.message_subscribe(partner_ids=partner_ids)

        # Poster un message d'approbation
        self.message_post(
            body=f"Dossier {self.name} approuvé avec succès.",
            subtype_xmlid='mail.mt_comment'
        )

        partner_ids = []
        if self.shipper_id.email:
            partner_ids.append(self.shipper_id.id)
        if self.consignee_id.email:
            partner_ids.append(self.consignee_id.id)

        if not partner_ids:
            raise UserError("Aucun email valide trouvé pour l'expéditeur ou le destinataire")

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_composition_mode': 'comment',
                'default_model': 'freight.operation',
                'default_res_ids': [int(self.id)],
                'default_partner_ids': [(6, 0, partner_ids)],
                'default_subject': f"Approbation du dossier {self.name}",
                'default_body': (
                    "<div style='font-family: Arial, sans-serif;'>"
                    "<p>Bonjour,</p>"
                    f"<p>Votre dossier <strong>{self.name}</strong> a été approuvé avec succès.</p>"
                    "<p>Merci pour votre collaboration.</p>"
                    "<p>Cordialement,</p>"
                    "<p>L'équipe logistique</p>"
                    "</div>"
                ),
            }
        }

    def action_reject(self):
        self.ensure_one()

        if not self.rejection_reason:
            raise UserError("Veuillez saisir un motif de rejet avant de continuer")

        if not (self.shipper_id.email or self.consignee_id.email):
            raise UserError("Aucun email valide trouvé pour l'expéditeur ou le destinataire")

        self.write({
            'state': 'rejected',
            'approver_id': self.env.user.id
        })

        partner_ids = []
        if self.shipper_id.email:
            partner_ids.append(self.shipper_id.id)
        if self.consignee_id.email:
            partner_ids.append(self.consignee_id.id)

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_composition_mode': 'comment',
                'default_model': 'freight.operation',
                'default_res_ids': [int(self.id)],
                'default_partner_ids': [(6, 0, partner_ids)],
                'default_subject': f"Rejet du dossier {self.name}",
                'default_body': (
                    "<div style='font-family: Arial, sans-serif;'>"
                    "<p>Bonjour,</p>"
                    f"<p>Votre dossier <strong>{self.name}</strong> a été rejeté pour le motif suivant :</p>"
                    f"<blockquote>{self.rejection_reason}</blockquote>"
                    "<p>Veuillez corriger ces éléments et soumettre à nouveau votre dossier.</p>"
                    "<p>Cordialement,</p>"
                    "<p>L'équipe logistique</p>"
                    "</div>"
                ),
            }
        }

    def action_request_info(self):
        self.ensure_one()

        if not (self.shipper_id.email or self.consignee_id.email):
            raise UserError("Aucun email valide trouvé pour l'expéditeur ou le destinataire")

        partner_ids = []
        if self.shipper_id.email:
            partner_ids.append(self.shipper_id.id)
        if self.consignee_id.email:
            partner_ids.append(self.consignee_id.id)

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_composition_mode': 'comment',
                'default_model': 'freight.operation',
                'default_res_ids': [int(self.id)],
                'default_partner_ids': [(6, 0, partner_ids)],
                'default_subject': f"Demande d'informations - Dossier {self.name}",
                'default_body': (
                    "<div style='font-family: Arial, sans-serif;'>"
                    "<p>Bonjour,</p>"
                    f"<p>Votre dossier <strong>{self.name}</strong> nécessite des informations complémentaires :</p>"
                    "<p>Merci de nous les fournir dans les plus brefs délais.</p>"
                    "<p>Cordialement,</p>"
                    "<p>L'équipe logistique</p>"
                    "</div>"
                ),
            }
        }

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'stage_id' in init_values:
            return self.env.ref('freight.mt_info_requested')
        return super()._track_subtype(init_values)
        
    @api.depends('task_ids.stage_id')
    def _compute_pending_tasks(self):
        done_stage = self.env.ref('custom_freight.project_stage_3')  # Stage "Terminé"
        for record in self:
            record.pending_task_count = len(record.task_ids.filtered(
                lambda t: t.stage_id != done_stage
            ))

    @api.model
    def create(self, vals):
        operation = super(FreightOperation, self).create(vals)
        
        # Vérifier si le module Project est installé
        if not self.env['ir.module.module'].search([('name','=','project'),('state','=','installed')]):
            return operation

        try:
            # Création du projet avec les bonnes valeurs par défaut
            project_vals = {
                'name': f"FREIGHT-{operation.name}",
                'partner_id': operation.shipper_id.id or operation.consignee_id.id,
                'description': f"Projet lié au dossier fret {operation.name}",
                'company_id': operation.company_id.id,
                'type_ids': [
                    (6, 0, [
                        self.env.ref('custom_freight.project_stage_1').id,  # À faire
                        self.env.ref('custom_freight.project_stage_2').id,  # En cours
                        self.env.ref('custom_freight.project_stage_3').id   # Terminé
                    ])
                ]
            }
            
            project = self.env['project.project'].sudo().create(project_vals)
            operation.project_id = project

            todo_stage = self.env.ref('custom_freight.project_stage_1')
            operation.with_context(default_stage_id=todo_stage.id)._generate_initial_tasks()
                        
        except Exception as e:
            _logger.error("Échec création projet pour %s: %s", operation.name, str(e))
            operation.message_post(
                body=f"Le projet associé n'a pas pu être créé: {str(e)}",
                subject="Erreur création projet"
            )
        
        return operation

    def _generate_initial_tasks(self):
        """Génère les tâches initiales selon le type d'opération"""
        self.ensure_one()

        todo_stage = self.env.context.get('default_stage_id') or self.env.ref('custom_freight.project_stage_1')

        # Tâche commune à tous les dossiers
        base_task = {
            'project_id': self.project_id.id,
            'company_id': self.company_id.id,
            'user_ids': [(6, 0, [self.env.user.id])],
            'stage_id': todo_stage.id if isinstance(todo_stage, int) else todo_stage.id,
            'date_deadline': fields.Date.today(),
        }
        
        tasks_to_create = [{
            'name': "Vérification des documents",
            'description': "Vérifier l'ensemble des documents du dossier",
        }]
        
        # Tâches spécifiques selon le mode de transport
        if self.transport == 'ocean':
            tasks_to_create.append({
                'name': "Réservation maritime",
                'description': "Réserver le transport maritime avec la compagnie",
            })
        elif self.transport == 'air':
            tasks_to_create.append({
                'name': "Réservation aérienne",
                'description': "Réserver le transport aérien",
            })
        elif self.transport == 'land':
            tasks_to_create.append({
                'name': "Planification transport",
                'description': "Organiser le transport routier",
            })
        
        # Création des tâches
        for task_vals in tasks_to_create:
            task_vals.update(base_task)
            self.env['project.task'].create(task_vals)

    def action_open_project(self):
        self.ensure_one()
        if not self.project_id:
            raise UserError("Aucun projet associé à ce dossier")
            
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.project_id.id,
            'views': [(False, 'form')],
            'target': 'current',
            'context': {
                'create': False,
                'edit': self.env.user.has_group('project.group_project_manager'),
            },
            'name': f"Projet {self.name}"
        }

    def action_generate_tasks(self):
        """Bouton pour regénérer les tâches si nécessaire"""
        self.ensure_one()
        if not self.project_id:
            raise UserError("Aucun projet associé à ce dossier")
            
        self._generate_initial_tasks()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Tâches générées",
                'message': f"Les tâches pour le dossier {self.name} ont été recréées",
                'type': 'success',
                'sticky': False,
            }
        }

    @api.constrains('stage_id')
    def _check_pending_tasks(self):
        """Empêche le passage aux étapes finales si tâches en attente"""
        closed_stages = self.env.ref('custom_freight.stage_declared') | self.env.ref('custom_freight.stage_closed')
        
        for operation in self:
            if operation.stage_id in closed_stages and operation.pending_task_count > 0:
                raise ValidationError(
                    f"Opération {operation.name} : {operation.pending_task_count} "
                    "tâche(s) non terminée(s). Complétez les tâches avant de continuer."
                )

    def action_mark_as_declared(self):
        self.ensure_one()
        if not self.env.user.has_group('custom_freight.group_freight_approver'):
            raise ValidationError("Vous n'avez pas les droits pour déclarer les opérations")
        self.write({'stage_id': self.env.ref('custom_freight.stage_declared').id})