import os
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CompanyVisit(models.Model):
    _name = 'company.visit'
    _description = 'Company Visit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'
    _order = 'visit_date desc'

    name = fields.Char('Visit Reference', required=True, copy=False, readonly=True, default='New')
    company_id = fields.Many2one('contracted.company', string='Company', required=True, tracking=True)
    visit_date = fields.Datetime('Visit Date', required=True, tracking=True)
    visitor_name = fields.Char('Visitor Name', required=True, tracking=True)
    visitor_position = fields.Char('Visitor Position', tracking=True)

    # Visit details
    purpose = fields.Selection([
        ('routine', 'Routine Inspection'),
        ('maintenance', 'Maintenance'),
        ('emergency', 'Emergency'),
        ('audit', 'Audit'),
        ('training', 'Training'),
        ('meeting', 'Meeting'),
        ('other', 'Other'),
    ], string='Visit Purpose', default='routine', required=True, tracking=True)

    duration_hours = fields.Float('Duration (Hours)', default=1.0, tracking=True)

    # Visit status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    # Visit findings and notes
    findings = fields.Html('Findings')
    recommendations = fields.Html('Recommendations')
    issues_found = fields.Html('Issues Found')
    actions_taken = fields.Html('Actions Taken')
    follow_up_required = fields.Boolean('Follow-up Required', tracking=True)
    follow_up_date = fields.Date('Follow-up Date')
    notes = fields.Text('Additional Notes')

    # Attachments and reports
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=', 'company.visit')],
                                     string='Attachments')

    # Computed fields
    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    visit_year = fields.Integer('Visit Year', compute='_compute_visit_year', store=True)
    visit_month = fields.Integer('Visit Month', compute='_compute_visit_month', store=True)
    pdf_report_generated = fields.Boolean('PDF Report Generated', default=False)
    report_file_path = fields.Char('Report File Path')

    @api.depends('name', 'company_id', 'visit_date')
    def _compute_display_name(self):
        for visit in self:
            if visit.company_id and visit.visit_date:
                date_str = visit.visit_date.strftime('%Y-%m-%d')
                visit.display_name = f"{visit.company_id.name} - {date_str} ({visit.name})"
            else:
                visit.display_name = visit.name or 'New Visit'

    @api.depends('visit_date')
    def _compute_visit_year(self):
        for visit in self:
            if visit.visit_date:
                visit.visit_year = visit.visit_date.year
            else:
                visit.visit_year = False

    @api.depends('visit_date')
    def _compute_visit_month(self):
        for visit in self:
            if visit.visit_date:
                visit.visit_month = visit.visit_date.month
            else:
                visit.visit_month = False

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('company.visit') or 'New'
        visit = super(CompanyVisit, self).create(vals)
        return visit

    def write(self, vals):
        result = super(CompanyVisit, self).write(vals)
        # If visit is completed and no PDF generated, generate it
        if vals.get('state') == 'completed':
            for visit in self:
                if not visit.pdf_report_generated:
                    visit.action_generate_pdf_report()
        return result

    def action_schedule(self):
        """Schedule the visit"""
        self.state = 'scheduled'

    def action_start_visit(self):
        """Start the visit"""
        self.state = 'in_progress'

    def action_complete_visit(self):
        """Complete the visit"""
        self.state = 'completed'
        # Auto-generate PDF report
        self.action_generate_pdf_report()

    def action_cancel_visit(self):
        """Cancel the visit"""
        self.state = 'cancelled'

    def action_reset_to_draft(self):
        """Reset to draft"""
        self.state = 'draft'

    def action_generate_pdf_report(self):
        """Generate PDF report for the visit - Simplified version"""
        if not self.company_id:
            raise UserError(_('Company is required to generate report.'))

        try:
            # Get the report and generate directly
            report = self.env.ref('contracted_companies_visits.action_report_visit')

            # Use the built-in report action - this handles all the complexity
            return report.report_action(self.ids)

        except Exception as e:
            _logger.error(f"Error generating PDF report for visit {self.name}: {str(e)}")
            raise UserError(_('Error generating PDF report: %s') % str(e))

    def action_view_report(self):
        """View the generated PDF report - Simplified version"""
        return self.action_generate_pdf_report()

    def action_view_report(self):
        """View the generated PDF report"""
        if not self.pdf_report_generated:
            return self.action_generate_pdf_report()

        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'company.visit'),
            ('res_id', '=', self.id),
            ('mimetype', '=', 'application/pdf')
        ], limit=1)

        if attachment:
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % attachment.id,
                'target': 'new',
            }
        else:
            return self.action_generate_pdf_report()

    @api.constrains('visit_date')
    def _check_visit_date(self):
        for visit in self:
            if visit.visit_date and visit.visit_date > fields.Datetime.now():
                if visit.state not in ['draft', 'scheduled']:
                    raise UserError(('Cannot set future date for visits that are not in draft or scheduled state.'))
