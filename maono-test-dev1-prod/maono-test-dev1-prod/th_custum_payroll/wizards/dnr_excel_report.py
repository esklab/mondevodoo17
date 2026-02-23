
import base64
import os
from datetime import datetime
from datetime import *
from io import BytesIO

import xlsxwriter
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from xlsxwriter.utility import xl_rowcol_to_cell


class payrollreportexcelwiz(models.TransientModel):
    _name = 'payroll.report.xlswiz'
    periode_id = fields.Many2one(
        'dnr.periode',
        string="Péroide",
    )

    annee = fields.Char(string="Année", default="2022")

    def generate_xlsx_report(self):
        payslip_ids = self.env['hr.payslip'].search([])
        mois_1 = self.periode_id.mois_ids[0].mois
        file_name = _('Rapprot de paie.xlsx')
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('payroll report.xlsx')
        worksheet.write(0, 3, "DECLARATION NOMINATIVE DES REMUNERATIONS")
        worksheet.write(2, 0, "Numéro Employeur")
        worksheet.write(
            2, 3, "Raison sociale : ZEN ROOTS TECHNOLOGIES")
        worksheet.write(3, 0, "Année : " + self.annee)
        worksheet.write(3, 2, "Trimestre: 1er")
        worksheet.write(3, 5, "Masse salariale :")
        worksheet.write(3, 6, "3000000")
        worksheet.write(3, 9, "Effectif : ")
        worksheet.write(3, 11, "Date traitement : ")
        worksheet.merge_range('A6:A7', "N° assurance")
        worksheet.merge_range('B6:B7', "Nom")
        worksheet.merge_range('C6:C7', "Prénoms")
        worksheet.merge_range('D6:D7', "Type assuré")
        n = 4
        for mois in self.periode_id.mois_ids:
            worksheet.write(5, n, mois.mois)
            worksheet.write(6, n, "Nbre jours")
            worksheet.write(6, n+1, "Rému nération")
            n = n + 2
        worksheet.merge_range('K6:K7', "Nature salaire")
        worksheet.merge_range('L6:L7', "Date embauche")
        worksheet.merge_range('M6:M7', "Date sortie")
        worksheet.merge_range('N6:N7', "Motif sortie")

        workbook.close()
        file_download = base64.b64encode(fp.getvalue())
        fp.close()
        self = self.with_context(
            default_name=file_name, default_file_download=file_download)

        return {
            'name': 'Télécharger la DNR',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payroll.report.excel',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self._context,
        }


class payroll_report_excel(models.TransientModel):
    _name = 'payroll.report.excel'
    name = fields.Char('Nom du fichier', size=256, readonly=True)
    file_download = fields.Binary('Telecharger la DNR', readonly=True)
