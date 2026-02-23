from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class NoteFrais(models.Model):
    _name = 'gestion_notes_frais.note_frais'
    _description = 'Note de frais'

    CATEGORIES = [
        ('transport', 'Transport'),
        ('logement', 'Logement'),
        ('communication', 'Communication'),
        ('deplacement', 'Deplacement Locaux'),
        ('liaison', 'Frais de Liaison'),
        ('indemnite', 'Indemnité Journalier'),
        # Ajoutez d'autres catégories au besoin
    ]

    CATEGORIES_EMP = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        # Ajoutez d'autres catégories au besoin
    ]
    
    ZONE_EMP = [
        ('ZA', 'Afrique Zone A'),
        ('ZB', 'Afrique Zone B'),
        ('ZOA', 'Hors Afrique'),
        # Ajoutez d'autres catégories au besoin
    ]

    ZONE_EMP_CONTINENT = [
        ('ZAF', 'Afrique'),
        ('ZEA', 'Zone Europe et Asie'),
        ('ZAM', 'Zone Amerique'),
        # Ajoutez d'autres catégories au besoin
    ]
    
    CATEGORIES_EMP_CREDIT = [
        ('GA', 'Groupe SocioProfessionel des Appuis'),
        ('GB', 'Categories P1 a P5 et E1'),
        ('GC', 'Categorie D et E2'),
        # Ajoutez d'autres catégories au besoin
    ]

    CATEGORIES_EMP_ALL = [
        ('TA', 'Tous les Employés'),
        ('CH', 'Chauffeur'),
    ]

    category = fields.Selection(CATEGORIES, string='Catégorie')
    description = fields.Char(string='Description')
    mission_id = fields.Many2one('project.task', string='Mission', required=True)
    
    @api.onchange('mission_id')
    def _onchange_mission_id(self):
        if self.mission_id:
            self.nom_hotel = self.mission_id.x_studio_nom_de_lhtel

    # Champs spécifiques à chaque catégorie...
    montant_declare_all = fields.Float(string='Montant Declare',compute='_compute_montant_total_logement',store=True,readonly=False)
    # Champs spécifiques à la catégorie Transport
    type_transport = fields.Selection([('aerien', 'Aérien'), ('maritime', 'Maritime'), ('routier', 'Routier')], string='Type de Transport')
    category_emp = fields.Selection(CATEGORIES_EMP, string='Catégorie Employee')
    category_emp_all = fields.Selection(CATEGORIES_EMP_ALL, string='Catégorie Employees')
    type_billet = fields.Selection([('affaires', 'Affaires'), ('economique', 'Économique'), ('intermediaire', 'Intermédiaire')], string='Type de Billet')
    montant_transport = fields.Float(string='Montant transport')
    reference_billet = fields.Char(string='Référence Billet')
    compagnie = fields.Char(string='Compagnie')
    montant_seuil = fields.Float(string='Montant Indiqué',compute='compute_montant_seuil',store=True)

    # Champs spécifiques à la catégorie Logement
    nom_hotel = fields.Char(string='Nom de l\'Hôtel', readonly=True)
    nombre_nuitees = fields.Integer(string='Nombre de Nuitées')
    montant_logement = fields.Float(string='Montant Logement')
    #montant_total_logement = fields.Float(string='Montant Total', compute='_compute_montant_total_logement', store=True)

    # Champs spécifiques à la catégorie Communication
    comm_duree = fields.Integer(string='Duree')
    comm_categorie = fields.Selection(CATEGORIES_EMP_CREDIT, string='Categorie Employee')
    #comm_montant = fields.Float(string='Montant Declaré')

    liaison_zone = fields.Selection(ZONE_EMP_CONTINENT, string='Pays/Region')
    #liaison_montant = fields.Float(string='Montant Declaré')

    deplacement_zone = fields.Selection(ZONE_EMP, string='Pays/Region')
    deplacement_duree = fields.Integer(string='Duree')
    #deplacement_montant = fields.Float(string='Montant Declaré')

    indemnite_duree = fields.Integer(string='Duree')
    indemnite_zone = fields.Selection(ZONE_EMP, string='Pays/Region')

    @api.model
    def create(self, vals):
        new_frais = super(NoteFrais, self).create(vals)
        task = self.env['project.task'].browse(vals['mission_id'])
        
        if not task:
            _logger.error("The mission with ID %s does not exist.", vals['mission_id'])
            raise ValueError("La mission spécifiée n'existe pas.")

        task_name = task.name
        task_description = task.description
        _logger.info(task_name)
        _logger.info(task_description)
        _logger.info(task.x_studio_personne_assigne)
        expense_name = new_frais.category
        montant = 0
        nom_hotel=task.x_studio_nom_de_lhtel
        _logger.info(nom_hotel)
        employee_id = task.x_studio_personne_assigne.id if task.x_studio_personne_assigne else False
        if not employee_id:
            _logger.error("The assigned employee must have an employee record.")
            raise ValueError("L'employé assigné à la mission doit avoir une fiche employé.")

        _logger.info("Creating expenses for category: %s", new_frais.category)
        if new_frais.category == "communication":
            montant = self.montant_communication(new_frais.comm_categorie, new_frais.comm_duree)
            new_frais.montant_seuil=montant
            _logger.error("montant = %s",montant)
            _logger.error("montant = %s",new_frais.montant_seuil)
            montant = new_frais.montant_seuil

            """if montant < new_frais.comm_montant:
                depassement_montant = new_frais.comm_montant - montant
                _logger.error("comm_montant = %s",new_frais.comm_montant)
                _logger.error("depassement_montant = %s",depassement_montant)
                new_expense = self.create_expense("Depassement " + expense_name, depassement_montant, employee_id)
            """
        elif new_frais.category == "liaison":
            montant = self.montant_liaison(new_frais.liaison_zone)
            new_frais.montant_seuil=montant
            _logger.error("montant = %s",montant)
            _logger.error("montant = %s",new_frais.montant_seuil)
            montant = new_frais.montant_seuil

            """if montant < new_frais.liaison_montant:
                depassement_montant = new_frais.liaison_montant - montant
                _logger.error("liaison_montant = %s",new_frais.liaison_montant)
                _logger.error("depassement_montant = %s",depassement_montant)
                new_expense = self.create_expense("Depassement " + expense_name, depassement_montant, employee_id)
            """

        elif new_frais.category == "deplacement":
            montant = self.montant_deplacement_locaux(new_frais.deplacement_zone, new_frais.deplacement_duree)
            new_frais.montant_seuil=montant
            _logger.error("montant = %s",montant)
            _logger.error("montant = %s",new_frais.montant_seuil)
            montant=new_frais.montant_seuil

            """if montant < new_frais.deplacement_montant:
                depassement_montant = new_frais.deplacement_montant - montant
                _logger.error("deplacement_montant = %s",new_frais.deplacement_montant)
                _logger.error("depassement_montant = %s",depassement_montant)
                new_expense = self.create_expense("Depassement " + expense_name, depassement_montant, employee_id)
            """

        elif new_frais.category == "indemnite":
            _logger.info("indemnite_zone = %s", new_frais.indemnite_zone)
            _logger.info("indemnite_zone = %s", new_frais.indemnite_duree)
            _logger.info("categorie_emp_all = %s", new_frais.category_emp_all)
            montant = self.montant_indemnite(new_frais.indemnite_zone, new_frais.category_emp_all)
            montant=montant*new_frais.indemnite_duree
            new_frais.montant_seuil=montant
            _logger.error("montant = %s", montant)
            _logger.error("montant seuil = %s",new_frais.montant_seuil)
            montant=new_frais.montant_seuil

        elif new_frais.category == "transport":
            montant = new_frais.montant_transport
            _logger.error("montant = %s",montant)

        elif new_frais.category == "logement":
            montant = new_frais.montant_logement
            new_frais.nom_hotel = nom_hotel
            _logger.error("montant = %s",new_frais.nom_hotel)
            montant_declare_all = montant * new_frais.nombre_nuitees
            _logger.error("montant = %s",montant)
            _logger.error("montant total = %s",montant_declare_all)
            montant=montant_declare_all
            
        new_expense = self.create_expense(expense_name, montant, employee_id)

        if new_expense:
            _logger.info("Associating expense with task: %s", task.name)
            task.x_studio_many2many_field_5r2_1hmcra6j0 |= new_expense
        return new_frais
    
    @api.depends('montant_logement', 'nombre_nuitees')
    def _compute_montant_total_logement(self):
        for record in self:
            record.montant_declare_all = record.montant_logement * record.nombre_nuitees
        else:
            record.montant_declare_all = record.montant_declare_all

    @api.onchange('indemnite_duree', 'deplacement_zone', 'deplacement_duree', 'liaison_zone', 'comm_categorie', 'comm_duree')
    def compute_montant_seuil(self):
        for record in self:
            if record.category == 'indemnite':
                montant = record.montant_indemnite(record.indemnite_zone, record.category_emp_all) * record.indemnite_duree
                record.montant_seuil = montant
            elif record.category == 'deplacement':
                montant = record.montant_deplacement_locaux(record.deplacement_zone, record.deplacement_duree)
                record.montant_seuil = montant
            elif record.category == 'liaison':
                montant = record.montant_liaison(record.liaison_zone)
                record.montant_seuil = montant
            elif record.category == 'communication' :
                montant = record.montant_communication(record.comm_categorie, record.comm_duree)
                record.montant_seuil = montant
            else:
                record.montant_seuil = 0

    def create_expense(self, name, amount, employee_id):
        _logger.info("Creating hr.expense record - Name: %s, Amount: %s, Employee ID: %s", name, amount, employee_id)
        expense = self.env['hr.expense'].create({
            'name': name,
            'total_amount_currency': amount,
            'employee_id': employee_id,
            # Ajoutez d'autres champs de hr.expense à initialiser ici
        })
        return expense
    
    def montant_communication(self, categorie, duree_mission):
        if categorie == 'GA':
            if duree_mission >= 1 and duree_mission <= 2:
                return 5000
            elif duree_mission >= 3 and duree_mission <= 4:
                return 10000
            elif duree_mission >= 5 and duree_mission <= 7:
                return 20000
            elif duree_mission >= 8 and duree_mission <= 10:
                return 30000
            elif duree_mission >= 11 and duree_mission <= 15:
                return 40000
            elif duree_mission >= 16 and duree_mission <= 1000000:
                return 50000
            else:
                return 0  # Valeur par défaut si la durée de la mission n'est pas dans les plages définies
        elif categorie == 'GB':
            if duree_mission >= 1 and duree_mission <= 2:
                return 10000
            elif duree_mission >= 3 and duree_mission <= 4:
                return 15000
            elif duree_mission >= 5 and duree_mission <= 7:
                return 30000
            elif duree_mission >= 8 and duree_mission <= 10:
                return 40000
            elif duree_mission >= 11 and duree_mission <= 15:
                return 50000
            elif duree_mission >= 16 and duree_mission <= 1000000:
                return 60000
            else:
                return 0
        elif categorie == 'GC':
            if duree_mission >= 1 and duree_mission <= 2:
                return 10000
            elif duree_mission >= 3 and duree_mission <= 4:
                return 15000
            elif duree_mission >= 5 and duree_mission <= 7:
                return 30000
            elif duree_mission >= 8 and duree_mission <= 10:
                return 50000
            elif duree_mission >= 11 and duree_mission <= 15:
                return 60000
            elif duree_mission >= 16 and duree_mission <= 100000:
                return 70000
            else:
                return 0 # Valeur par défaut si la catégorie n'est pas reconnue

    def montant_deplacement_locaux(self, categorie, duree_mission):
        if categorie == 'ZA':
            if duree_mission >= 1 and duree_mission <= 2:
                return 15000
            elif duree_mission >= 3 and duree_mission <= 4:
                return 20000
            elif duree_mission >= 5 and duree_mission <= 7:
                return 25000
            elif duree_mission >= 8 and duree_mission <= 10:
                return 35000
            elif duree_mission >= 11 and duree_mission <= 15:
                return 45000
            elif duree_mission >= 16 and duree_mission <= 1000000:
                return 55000
            else:
                return 0  # Valeur par défaut si la durée de la mission n'est pas dans les plages définies
        elif categorie == 'ZB' or categorie == 'ZOA':
            if duree_mission >= 1 and duree_mission <= 2:
                return 20000
            elif duree_mission >= 3 and duree_mission <= 4:
                return 25000
            elif duree_mission >= 5 and duree_mission <= 7:
                return 35000
            elif duree_mission >= 8 and duree_mission <= 10:
                return 45000
            elif duree_mission >= 11 and duree_mission <= 15:
                return 55000
            elif duree_mission >= 16 and duree_mission <= 1000000:
                return 65000
            else:
                return 0

    def montant_liaison(self, categorie):
        if categorie == 'ZAF':
            return 25000
        elif categorie == 'ZEA':
            return (160*655)
        elif categorie == 'ZAM':
            return (215*600)
        else:
            return 0

    def montant_indemnite(self,zone,categorie_emp_all):
        if categorie_emp_all == 'TA':
            if zone == 'ZA':
                return 50000
            elif zone == 'ZB':
                return 75000
            elif zone == 'ZOA':
                return 100000
            else:
                return 0
        elif categorie_emp_all == 'CH':
            if zone == 'ZA':
                return 40000
            elif zone == 'ZB':
                return 40000
            elif zone == 'ZOA':
                return 40000
            else:
                return 40000
        else:
            return 0