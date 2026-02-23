from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DockPrice(models.Model):
    _name = 'dock.price'
    _description = 'Prix d\'Acconage et Relevage'

    name = fields.Char(string="Référence", default="/")
    type = fields.Selection([('import', 'Import'), ('export', 'Export')], default=False,
                            required=True)
    service_type = fields.Selection([
        ('acconage', 'Acconage'),
        ('relevage', 'Relevage'),
    ], string="Type de Service", required=True)
    dock_category_id = fields.Many2one(
        'dock.category',
        string='Catégorie Acconage',
        required=True,
        tracking=True,
        index=True,
    )
    category_id = fields.Many2one('product.category', string="Catégorie d'Article", required=True)
    container_type_id = fields.Many2one('container.type', string="Type de Conteneur", required=True)
    year = fields.Char(string="Année", required=True, help="Année d'application de ce prix, au format AAAA")
    price = fields.Float(string="Prix", required=True,
                         help="Prix en fonction du service, de l'article, et du conteneur")
    is_active = fields.Boolean(string="En vigueur", default=True, help="Le prix est-il en cours d'application ?")
    history_ids = fields.One2many('dock.price.history', 'dock_price_id', string="Historique des Prix")

    @api.depends('service_type', 'category_id', 'container_type_id', 'year')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.service_type.upper()} - {record.category_id.name} - {record.container_type_id.name} ({record.year})"

    @api.constrains('year')
    def _check_year_format(self):
        for record in self:
            if not record.year.isdigit() or len(record.year) != 4:
                raise ValidationError("L'année doit être au format AAAA (exemple : 2024)")

    @api.model
    def get_default_price(self, service_type, category_id, container_type_id):
        """Retourne le prix par défaut en fonction du service, de la catégorie et du type de conteneur"""
        current_year = fields.Date.today().year
        price = self.search([
            ('service_type', '=', service_type),
            ('category_id', '=', category_id),
            ('container_type_id', '=', container_type_id),
            ('year', '=', str(current_year)),
            ('is_active', '=', True)
        ], limit=1)
        return price.price if price else 0.0

    # def write(self, vals):
    #     """Stocker l'ancien prix dans l'historique avant mise à jour"""
    #     if 'price' in vals:  # Vérifie si le prix change
    #         for record in self:
    #             # Ajouter l'ancien prix dans l'historique
    #             self.env['dock.price.history'].create({
    #                 'dock_price_id': record.id,
    #                 'service_type': record.service_type,
    #                 'category_id': record.category_id.id,
    #                 'container_type_id': record.container_type_id.id,
    #                 'year': record.year,
    #                 'previous_price': record.price,
    #                 'updated_date': fields.Datetime.now(),
    #             })
    #     return super(DockPrice, self).write(vals)


class DockPriceHistory(models.Model):
    _name = 'dock.price.history'
    _description = 'Historique des Prix'

    dock_price_id = fields.Many2one('dock.price', string="Lien au Prix d'Origine", required=True, ondelete='cascade')
    service_type = fields.Selection([
        ('acconage', 'Acconage'),
        ('relevage', 'Relevage'),
    ], string="Type de Service", required=True)
    category_id = fields.Many2one('product.category', string="Catégorie d'Article", required=True)
    container_type_id = fields.Many2one('container.type', string="Type de Conteneur", required=True)
    year = fields.Char(string="Année", required=True, help="Année d'application de ce prix")
    previous_price = fields.Float(string="Prix Ancien", required=True)
    updated_date = fields.Datetime(string="Date de Modification", required=True, default=fields.Datetime.now)
