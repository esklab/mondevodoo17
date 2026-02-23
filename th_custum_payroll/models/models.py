# -*- coding: utf-8 -*-

from odoo import models, api, _, fields
from odoo.exceptions import UserError, ValidationError
from math import *
from datetime import *
import datetime
import dateutil
from dateutil.relativedelta import relativedelta


class hrContactInherit(models.Model):
    _inherit = 'hr.contract'

    heure_sup_20 = fields.Float(
        string='HEURES SUPP 20%',
        default=0,
    )
    heure_sup_40 = fields.Float(
        string='HEURES SUPP 40%',
        default=0,
    )
    heure_sup_65 = fields.Float(
        string='HEURES SUPP 65%',
        default=0,
    )
    heure_sup_100 = fields.Float(
        string='HEURES SUPP 100%',
        default=0,
    )
    heure_sup_nuit = fields.Float(
        string='HEURES SUPP NUIT',
        default=0,
    )
    adjustement = fields.Float(
	    string='Ajustement de salaire net',
	    default=0,
	)
    taux_horaire = fields.Float(string="Taux horaire")
    nombre_jour = fields.Float(string="Nombre de jour travaillés")
    contrat_declare = fields.Boolean(string="Contrat déclaré")
    salary_advance = fields.Float(string="Avance sur salaire", help="Montant total de l'avance sur salaire")
    repayment_months = fields.Integer(
        string="Nombre de mois",
        help="Durée en mois pour rembourser l'avance",
        compute="_compute_repayment_months",
        inverse="_set_repayment_months",
        store=True,
    )
    monthly_repayment = fields.Float(
        string="Remboursement mensuel",
        compute="_compute_monthly_repayment",
        inverse="_set_monthly_repayment",
        store=True,
        help="Montant remboursé chaque mois"
    )
    manual_entry = fields.Boolean(string="Saisie manuelle", default=False,
                                  help="Indique si une valeur a été saisie manuellement.")
    advance_date_start = fields.Date(
        string="Date de début",
        help="Date de début de remboursement"
    )
    advance_date_end = fields.Date(
        string="Date de fin",
        compute="_compute_date_end",
        store=True,
        help="Date de fin de remboursement")

    appel_urgence = fields.Float(
	    string="Appel d'urgence",
	    default=0,
	)
    astreinte = fields.Float(
	    string='Astreinte',
	    default=0,
	)
    conge_sans_solde = fields.Float(
	    string='Nbr de jrs de congé sans solde',
	    default=0,
	)
    prime_transport = fields.Float(
	    string='Prime de transport',
	    default=0,
	)
    prime_caisse = fields.Float(
	    string='Prime de caisse',
	    default=0,
	)
    prime_garde = fields.Float(
	     string='Prime de garde',
	     default=0,
	)
    prime_panier = fields.Float(
	    string='Prime de panier',
	    default=0,
	)
    prime_risque = fields.Float(
	    string='Prime de risque',
	)
    prime_salisure = fields.Float(
		string="Prime de salissure"
	)
    prime_resultat = fields.Float(string="Prime de resultat")
    prime_speciale = fields.Float(
	    string='Prime spéciale',
	)
    prime_fonction = fields.Float(string="Prime de fonction")
    prime_specialite = fields.Float(
	    string='Prime de spécialité',
	)
    prime_responsabilite = fields.Float(
	    string='Prime de responsabilté',
	)
    rapel_salaire_imp = fields.Float(
	    string='Rappel de salaire imposable',
	)
    remboursement_pret = fields.Float(
	    string='Remboursement de prêt',
	)
    sursalaire = fields.Float(
	    string='Sursalaire',
	)
    regularisation_salaire_net = fields.Float(
		string="Régularisation salaire net",
	)
    trop_percu = fields.Float(
	    string='Trop perçu sur prime',
	)
    prime_logement = fields.Float(string="Prime de logement")
    prime_logement_10 = fields.Float(string="Prime de logement 10%")
    prime_13_mois = fields.Float(string="13ème mois")
    conge_paye = fields.Float(string="Congé payé/technique")
    indeminite_retraite_ir = fields.Float(string="Indemnité de retraite 50% A IR")
    indeminite_retraite_non_ir = fields.Float(string="Indemnité de retraite 50% non IR")
    relevement_salaire = fields.Float(string="Relevement de salaire")
    indeminite_compens = fields.Float(string="Indemnité de compens")
    commission = fields.Float(string="Commission")
    avantage_logement = fields.Float(string="Avantage en nature logement")
    avantage_voiture = fields.Float(string="Avantage en nature voiture")
    preavis = fields.Float(string="Préavis")
    precues_salaire = fields.Float(string="Percues sur salaire")
    indemnite_licenciement = fields.Float(string="Indemnité de licencement")
    autres_primes = fields.Float(string="Autres primes")
    habillement_encouragement = fields.Float(string="Habillement et encouragement")
    frais_forfait_remboursement = fields.Float(string="Frais forf remboursement")
    indemnite_non_imposable = fields.Float(string="Indemnité non imposable")
    indemnite_licenciement_35 = fields.Float(string="Indemnité de licencement 35%")
    indemnite_licenciement_40 = fields.Float(string="Indemnité de licencement 40%")
    indemnite_licenciement_45 = fields.Float(string="Indemnité de licencement 45%")
    retenue_syndicat = fields.Float(string="Retenue syndicat")
    retenue_assurance_maladie = fields.Float(string="Retenue assurance maladie")
    avance_accompte_retenues = fields.Float(string="Avance et accompte retenues")
    avance_retenue_13_hon = fields.Float(string="Avance retenue 13ème mois hon")
    absence_a_deduire = fields.Float(string="Absence à déduire")


    type_paiement = fields.Selection([
        ('espece','Espèce'),
        ('virement','Virement'),
        ('cheque','Chèque banciare'),
	], string="Type de paiement", default="virement")

    est_cadre = fields.Boolean(string="Est cadre ?")

    @api.depends('salary_advance', 'repayment_months')
    def _compute_monthly_repayment(self):
        for contract in self:
            if not contract.manual_entry and contract.salary_advance > 0 and contract.repayment_months > 0:
                contract.monthly_repayment = contract.salary_advance / contract.repayment_months

    def _set_monthly_repayment(self):
        for contract in self:
            if contract.salary_advance > 0 and contract.monthly_repayment > 0:
                contract.repayment_months = int(contract.salary_advance / contract.monthly_repayment)
                contract.manual_entry = True

    @api.depends('salary_advance', 'monthly_repayment')
    def _compute_repayment_months(self):
        for contract in self:
            if not contract.manual_entry and contract.salary_advance > 0 and contract.monthly_repayment > 0:
                contract.repayment_months = int(contract.salary_advance / contract.monthly_repayment)

    def _set_repayment_months(self):
        for contract in self:
            if contract.salary_advance > 0 and contract.repayment_months > 0:
                contract.monthly_repayment = contract.salary_advance / contract.repayment_months
                contract.manual_entry = True

    @api.depends('advance_date_start', 'repayment_months')
    def _compute_date_end(self):
        """Calcul de la date de fin basé sur la date de début et le nombre de mois."""
        for record in self:
            if record.advance_date_start and record.repayment_months > 0:
                record.advance_date_end = record.advance_date_start + relativedelta(months=record.repayment_months)
            else:
                record.advance_date_end = False

    @api.onchange('wage')
    def onchange_wage(self):
        for rec in self:
            rec.taux_horaire = (rec.wage + rec.sursalaire) / 173.33

    @api.model
    def _cron_update_experience_years(self):
        """
        Méthode à exécuter via un cron job quotidien pour mettre à jour
        les années d'expérience des contrats actifs
        """
        contracts = self.search([('state', '=', 'open')])

        for contract in contracts:
            if contract.date_start:
                start_date = fields.Date.from_string(contract.date_start)
                today = fields.Date.today()

                # Calcul de la différence en années
                years_diff = relativedelta(today, start_date).years

                # Mise à jour uniquement si le nombre d'années a changé
                if years_diff != contract.x_studio_anne_dexprience_dans_ce_domaine:
                    contract.write({
                        'x_studio_anne_dexprience_dans_ce_domaine': years_diff
                    })


class hrPersoneACharge(models.Model):
    _name = 'hr.personne.acharge'
    _description = 'Personne à charge'

    name = fields.Char(
        string='Nom et prénom(s)',
        required=True,
    )
    date_naissance = fields.Date(string="Date de naissance")
    age = fields.Integer(
        string='Age',
        store=True,
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Personne à charge',
    )

    @api.onchange('date_naissance')
    def _calculer_age(self):
        for rec in self:
            if type(rec.date_naissance) != bool:
                today_year = datetime.datetime.today().year
                birth_year = rec.date_naissance.year
                age = today_year - birth_year
                rec.age = age


class hrEmployeInherit(models.Model):
    _inherit = 'hr.employee'

    persone_acharge_ids = fields.One2many(
        'hr.personne.acharge',
        'employee_id',
        string='Personnes à charge',
    )
    numero_cnss = fields.Char(
        string="Numéro de CNSS",
    )
    matricule = fields.Char(
        string='Numéro matricule',
    )
    payslip_ids = fields.One2many(
        'hr.payslip',
        'employee_id',
        string='Field Label',
    )
    heure_travail = fields.Float(
        string="Nombre d'heure de travail",
    )
    account_number = fields.Char(
        string="Numéro de compte"
    )
    banque_id = fields.Many2one(
        'res.bank',
        string='banque',
        )
    indice = fields.Float(
        string="Indice"
    )
    valeur_indice = fields.Float(
        string="Valeur indice"
    )
    leave_ids = fields.One2many('hr.leave', 'employee_id', string="Congés")
    allocation_ids = fields.One2many('hr.leave.allocation', 'employee_id', string="Allocations")

    est_un_gerant = fields.Boolean(string="Est un gérant")

    annual_leave_balance = fields.Float(
        string="Solde Congés Annuels",
        compute="_compute_annual_leave_balance",
        store=True,
    )

    @api.depends(
        'leave_ids.state',  # Dépend du statut des congés
        'leave_ids.number_of_days',  # Dépend du nombre de jours de congés
        'allocation_ids.state',  # Dépend du statut des allocations
        'allocation_ids.number_of_days',  # Dépend du nombre de jours alloués
    )
    def _compute_annual_leave_balance(self):
        for employee in self:
            # Récupérer les allocations validées pour les congés annuels
            allocations = self.env['hr.leave.allocation'].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'validate'),
                ('holiday_status_id.name', '=', 'Congés annuels'),
            ])
            # Récupérer les congés validés pour les congés annuels
            leaves = self.env['hr.leave'].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'validate'),
                ('holiday_status_id.name', '=', 'Congés annuels'),
            ])
            # Calculer le solde : allocations - congés pris
            allocated_days = sum(allocations.mapped('number_of_days'))
            taken_days = sum(leaves.mapped('number_of_days'))
            employee.annual_leave_balance = allocated_days - taken_days

    @api.onchange('persone_acharge_ids')
    def onchange_persone_acharge_ids(self):
        for rec in self:
            rec.children = len(rec.persone_acharge_ids)


class RubriqueLine(models.Model):
    _name = 'rubrique.lier'
    _description = 'Description'

    nom = fields.Char(
        string='Rubrique',
    )
    montant = fields.Char(
        string='Montant',
    )




class HrPayslip(models.Model):

    _inherit = 'hr.payslip'
    anciennete = fields.Float(string="Ancienneté")
    net_wage = fields.Float(string="Salaire net", compute="get_salaire_net")
    heure_suplementaire = fields.Float(string="Heure suplémentaire")

    def compute_sheet(self):
        result = super().compute_sheet()
        self.get_salaire_net()
        return result

    def get_salaire_net(self):
        for rec in self:
            total = 0
            for line in rec.line_ids:
                if line.sequence == 2000:
                    total += line.total
            rec.net_wage = total

    @api.onchange('contract_id','employee_id')
    def calcule_anciennete(self):
        for rec in self:
            date_debut = rec.contract_id.date_start
            date_fin = rec.date_to
            if date_debut and date_fin:
                datef = date_debut.strftime('%Y,%m,%d')
                dated = date_fin.strftime('%Y,%m,%d')
                n1 = datef.split(',')
                n2 = dated.split(',')
                d0 = datetime.date(int(n1[0]),int(n1[1]),int(n1[2]))
                d1 = datetime.date(int(n2[0]),int(n2[1]),int(n2[2]))
                deltat = d1 - d0
                annee = (deltat.days) / 365
                mois = ((deltat.days) - int(annee) * 365)/30
                rec.anciennete = deltat.days
            hs = rec.contract_id.heure_sup_20 + rec.contract_id.heure_sup_40 + rec.contract_id.heure_sup_65 + rec.contract_id.heure_sup_100 + rec.contract_id.heure_sup_nuit 
            rec.heure_suplementaire = hs