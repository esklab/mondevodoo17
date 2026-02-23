# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class ACSHospitalization(models.Model):
    _inherit = "acs.hospitalization"

    def acs_hospitalization_physician_round_data(self, invoice_id=False):
        _logger.info("=== DEBUT acs_hospitalization_physician_round_data ===")
        _logger.info("Hospitalisation ID: %s", self.id)
        _logger.info("Invoice ID fourni: %s", invoice_id)
        
        product_data = super(ACSHospitalization, self).acs_hospitalization_physician_round_data(invoice_id)
        _logger.info("Données de produit initiales: %s", product_data)
        
        ward_rounds_to_invoice = self.physician_ward_round_ids.filtered(lambda s: not s.invoice_id)
        _logger.info("Rondes médicales à facturer trouvées: %d", len(ward_rounds_to_invoice))
        
        if ward_rounds_to_invoice:
            ward_data = {}
            for ward_round in ward_rounds_to_invoice:
                _logger.debug("Traitement de la ronde ID: %s", ward_round.id)
                
                if ward_round.physician_id:
                    _logger.debug("Médecin trouvé: %s (ID: %s)", 
                                ward_round.physician_id.name, 
                                ward_round.physician_id.id)
                    
                    if ward_round.physician_id.ward_round_service_id:
                        product = ward_round.physician_id.ward_round_service_id
                        physician_name = ward_round.physician_id.name or ''
                        _logger.debug("Service de ronde trouvé: %s (ID: %s)", 
                                      product.name, product.id)
                        
                        if product in ward_data:
                            ward_data[product]['quantity'] += 1
                            ward_data[product]['physicians'].add(physician_name)
                            _logger.debug("Produit existant mis à jour dans ward_data")
                        else:
                            ward_data[product] = {
                                'product_id': product,
                                'quantity': 1,
                                'physicians': set([physician_name]),
                                'name': _("Physician Ward Round Charges")
                            }
                            _logger.debug("Nouveau produit ajouté à ward_data")
                    else:
                        _logger.warning("Aucun service de ronde défini pour le médecin %s", 
                                      ward_round.physician_id.name)
                else:
                    _logger.warning("Aucun médecin associé à la ronde ID: %s", ward_round.id)
            
            _logger.info("Données de ronde compilées: %s", ward_data)
            
            product_data = []
            for product in ward_data.values():
                physicians = ', '.join(product['physicians'])
                _logger.debug("Création de ligne pour les médecins: %s", physicians)
                
                product_data.append({
                    'name': _("Physician Ward Round Charges - %s") % physicians,
                })
                product_data.append({
                    'product_id': product['product_id'],
                    'quantity': product['quantity'],
                    'name': _("Visits by: %s") % physicians,
                })

            if invoice_id:
                ward_rounds_to_invoice.invoice_id = invoice_id.id
                _logger.info("Invoice ID %s associé aux rondes médicales", invoice_id.id)
        
        _logger.info("Données de produit finales: %s", product_data)
        _logger.info("=== FIN acs_hospitalization_physician_round_data ===")
        return product_data

    def get_surgery_invoice_data(self, invoice_id=False):
        _logger.info("=== DEBUT get_surgery_invoice_data ===")
        _logger.info("Hospitalisation ID: %s", self.id)
        
        product_data = super(ACSHospitalization, self).get_surgery_invoice_data(invoice_id)
        _logger.info("Données de chirurgie initiales: %s", product_data)
        
        surgery_ids = self.surgery_ids.filtered(lambda s: not s.invoice_id)
        _logger.info("Chirurgies à facturer trouvées: %d", len(surgery_ids))
        
        if surgery_ids:
            product_data = []
            for surgery in surgery_ids:
                _logger.debug("Traitement de la chirurgie ID: %s", surgery.id)
                
                physician_name = surgery.physician_id.name if surgery.physician_id else _("No surgeon")
                _logger.debug("Chirurgien trouvé: %s", physician_name)
                
                product_data.append({
                    'name': _("Surgical Procedure - %s") % physician_name,
                })
                
                for line in surgery.surgery_line_ids:
                    if line.product_id:
                        _logger.debug("Ligne de chirurgie trouvée - Produit: %s", line.product_id.name)
                        product_data.append({
                            'product_id': line.product_id,
                            'quantity': line.qty,
                            'name': _("%s (Surgeon: %s)") % (line.product_id.name, physician_name),
                        })
                    else:
                        _logger.warning("Ligne de chirurgie sans produit - ID: %s", line.id)
            
            if invoice_id:
                surgery_ids.invoice_id = invoice_id.id
                _logger.info("Invoice ID %s associé aux chirurgies", invoice_id.id)
        
        _logger.info("Données de chirurgie finales: %s", product_data)
        _logger.info("=== FIN get_surgery_invoice_data ===")
        return product_data