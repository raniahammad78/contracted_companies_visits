import os
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ContractedCompany(models.Model):
    _name = 'contracted.company'
    _description = 'Contracted Company'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char('Company Name', required=True, tracking=True)
    code = fields.Char('Company Code', required=True, tracking=True)
    contact_person = fields.Char('Contact Person', tracking=True)
    phone = fields.Char('Phone', tracking=True)
    email = fields.Char('Email', tracking=True)
    address = fields.Text('Address', tracking=True)
    contract_start_date = fields.Date('Contract Start Date', tracking=True)
    contract_end_date = fields.Date('Contract End Date', tracking=True)
    visits_per_month = fields.Integer('Visits per Month', default=1, tracking=True)
    active = fields.Boolean('Active', default=True, tracking=True)
    notes = fields.Text('Notes')

    # Computed fields
    visit_count = fields.Integer('Total Visits', compute='_compute_visit_statistics')
    current_year_visits = fields.Integer('Current Year Visits', compute='_compute_visit_statistics')
    expected_yearly_visits = fields.Integer('Expected Yearly Visits', compute='_compute_expected_visits')
    folder_path = fields.Char('Folder Path', compute='_compute_folder_path')

    # Visit statistics
    last_visit_date = fields.Datetime('Last Visit', compute='_compute_visit_statistics')
    next_scheduled_visit = fields.Datetime('Next Scheduled Visit', compute='_compute_visit_statistics')

    @api.depends('visits_per_month')
    def _compute_expected_visits(self):
        for company in self:
            company.expected_yearly_visits = company.visits_per_month * 12

    @api.depends('name', 'code')
    def _compute_folder_path(self):
        for company in self:
            if company.name and company.code:
                # Clean the name for folder creation
                clean_name = "".join(c for c in company.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                company.folder_path = f"Company_Visits/{company.code}_{clean_name}"
            else:
                company.folder_path = ''

    def _compute_visit_statistics(self):
        current_year = fields.Date.today().year
        for company in self:
            visits = self.env['company.visit'].search([('company_id', '=', company.id)])
            current_year_visits = visits.filtered(lambda v: v.visit_date and v.visit_date.year == current_year)

            company.visit_count = len(visits)
            company.current_year_visits = len(current_year_visits)

            if visits:
                completed_visits = visits.filtered(lambda v: v.state == 'completed' and v.visit_date)
                if completed_visits:
                    company.last_visit_date = max(completed_visits.mapped('visit_date'))
                else:
                    company.last_visit_date = False

                scheduled_visits = visits.filtered(lambda v: v.state == 'scheduled' and v.visit_date)
                if scheduled_visits:
                    company.next_scheduled_visit = min(scheduled_visits.mapped('visit_date'))
                else:
                    company.next_scheduled_visit = False
            else:
                company.last_visit_date = False
                company.next_scheduled_visit = False

    @api.model
    def create(self, vals):
        company = super(ContractedCompany, self).create(vals)
        company._create_company_folders()
        return company

    def write(self, vals):
        result = super(ContractedCompany, self).write(vals)
        if 'name' in vals or 'code' in vals:
            for company in self:
                company._create_company_folders()
        return result

    def _create_company_folders(self):
        """Create folder structure for the company"""
        if not self.folder_path:
            return

        try:
            # Get the base directory (you might want to configure this in settings)
            base_dir = self.env['ir.config_parameter'].sudo().get_param('company_visits.base_directory',
                                                                        '/tmp/company_visits')

            company_folder = os.path.join(base_dir, self.folder_path)

            # Create main company folder
            os.makedirs(company_folder, exist_ok=True)

            # Create year folders (current year and next year)
            current_year = fields.Date.today().year
            for year in range(current_year, current_year + 2):
                year_folder = os.path.join(company_folder, str(year))
                os.makedirs(year_folder, exist_ok=True)

            _logger.info(f"Created folder structure for company {self.name} at {company_folder}")

        except Exception as e:
            _logger.error(f"Error creating folders for company {self.name}: {str(e)}")
            # Don't raise an error as this shouldn't block the creation/update

    def action_view_visits(self):
        """Action to view all visits for this company"""
        return {
            'name': ('Visits - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'company.visit',
            'view_mode': 'list,form,calendar,graph',
            'domain': [('company_id', '=', self.id)],
            'context': {
                'default_company_id': self.id,
            }
        }

    def action_schedule_visit(self):
        """Action to schedule a new visit"""
        return {
            'name': ('Schedule Visit'),
            'type': 'ir.actions.act_window',
            'res_model': 'company.visit',
            'view_mode': 'form',
            'context': {
                'default_company_id': self.id,
                'default_visit_date': fields.Datetime.now(),
            },
            'target': 'new',
        }

    @api.constrains('code')
    def _check_code_unique(self):
        for company in self:
            if company.code:
                existing = self.search([
                    ('code', '=', company.code),
                    ('id', '!=', company.id)
                ])
                if existing:
                    raise UserError(('Company code must be unique. Code "%s" already exists.') % company.code)