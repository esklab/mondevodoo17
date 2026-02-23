from odoo import fields, models, api, exceptions


class WorkflowTransition(models.Model):
    _name = 'workflow.transition'
    _description = 'Transition de Workflow'

    name = fields.Char(string='Nom', required=True)
    workflow_id = fields.Many2one('workflow.model', string='Workflow', required=True)
    from_state = fields.Many2one('workflow.state', string='État Source', required=True)
    to_state = fields.Many2one('workflow.state', string='État Cible', required=True)
    allowed_groups = fields.Many2many('res.groups', string='Groupes Autorisés')
    condition = fields.Text(string='Condition Python',
                            help="Condition Python optionnelle qui doit être vraie pour permettre la transition. "
                                 "Utiliser 'record' pour accéder à l'enregistrement.")
    send_notification = fields.Boolean(string="Envoyer notification", default=True)
    send_email = fields.Boolean(string="Envoyer email", default=False)

    @api.constrains('from_state', 'to_state')
    def _check_different_states(self):
        for transition in self:
            if transition.from_state == transition.to_state:
                raise exceptions.ValidationError("Les états source et cible doivent être différents.")

    def _check_condition(self, record):
        """Évalue la condition Python sur l'enregistrement"""
        if not self.condition:
            return True

        try:
            localdict = {'record': record, 'env': self.env}
            return eval(self.condition, {'__builtins__': {}}, localdict)
        except Exception as e:
            raise exceptions.UserError(f"Erreur lors de l'évaluation de la condition: {str(e)}")

    def apply_transition(self, record):
        # Vérifier que l'utilisateur a les droits d'écriture sur l'enregistrement
        if not record.check_access_rights('write', False) or not record.check_access_rule('write'):
            raise exceptions.AccessError("Vous n'avez pas les droits d'écriture sur cet enregistrement.")

        # Vérifier l'état actuel
        if record[self.workflow_id.state_field] != self.from_state.code:
            raise exceptions.UserError("La transition n'est pas possible depuis l'état actuel.")

        # Vérifier les groupes de l'utilisateur
        user_groups_ids = self.env.user.groups_id.ids
        if self.allowed_groups and not any(group.id in user_groups_ids for group in self.allowed_groups):
            raise exceptions.AccessError("Vous n'avez pas l'autorisation pour effectuer cette transition.")

        # Vérifier la condition
        if not self._check_condition(record):
            raise exceptions.UserError("Les conditions pour cette transition ne sont pas remplies.")

        # Appliquer la transition
        record.write({self.workflow_id.state_field: self.to_state.code})

        # Ajouter la demande de validation dans la corbeille unique
        self.env['workflow.trash'].create({
            'name': f"Validation pour {record._name} ({record.id})",
            'model_name': record._name,
            'record_id': record.id,
            'state': self.to_state.code,
            'requested_by': self.env.user.id,
            'transition_id': self.id,
        })

        # Historiser la validation
        history_record = self.env['workflow.history'].create({
            'transition_id': self.id,
            'record_id': record.id,
            'model_name': record._name,
            'validated_by': self.env.user.id,
            'old_state': self.from_state.code,
            'new_state': self.to_state.code,
        })

        # Gestion des notifications
        if self.send_notification or self.send_email:
            self._send_notifications(record, history_record)

        return True

    def _send_notifications(self, record, history_record):
        """Envoie des notifications et emails aux utilisateurs concernés"""
        # Récupérer tous les utilisateurs uniques des groupes autorisés
        users_to_notify = self.env['res.users']
        if self.allowed_groups:
            domain = [('groups_id', 'in', self.allowed_groups.ids)]
            users_to_notify = self.env['res.users'].search(domain)

        if not users_to_notify:
            return

        # Préparation des messages
        subject = f'Validation de {record.display_name or record._name}'
        body = f"""
            <p>Une transition de workflow a été effectuée:</p>
            <ul>
                <li>Enregistrement: {record.display_name or f"{record._name} ({record.id})"}</li>
                <li>Transition: {self.name}</li>
                <li>Nouvel état: {self.to_state.name}</li>
                <li>Effectuée par: {self.env.user.name}</li>
            </ul>
        """

        # Notifications internes
        if self.send_notification:
            partner_ids = users_to_notify.mapped('partner_id').ids

            self.env['mail.message'].create({
                'subject': subject,
                'body': body,
                'res_id': record.id,
                'model': record._name,
                'message_type': 'notification',
                'subtype_id': self.env.ref('mail.mt_note').id,
                'partner_ids': [(6, 0, partner_ids)]
            })

        # Emails
        if self.send_email:
            for user in users_to_notify:
                if user.email:
                    mail_values = {
                        'subject': subject,
                        'body_html': body,
                        'email_to': user.email,
                        'auto_delete': True,
                    }
                    self.env['mail.mail'].create(mail_values).send()

