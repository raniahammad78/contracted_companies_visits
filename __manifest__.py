{
    'name': 'Company Visits Management',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'category': 'Services',
    'summary': 'Manage contracted company visits with automatic PDF reports and folder organization',
    'description': """
Company Visits Management
=========================

This module provides functionality to:
* Manage contracted companies
* Schedule and track visits
* Generate automatic PDF reports for each visit
* Create automatic folder structure for companies
* Organize visits by year in sub-folders
* Track visit statistics and totals

Features:
- Automatic folder creation for each company
- Year-based sub-folder organization
- PDF report generation for visits
- Visit scheduling and tracking
- Monthly and yearly visit statistics
- Visit status management
    """,
    'author': 'RANIA',
    'depends': ['base', 'mail'],
    'data': [
        "reports/visit_report.xml",
        "reports/visit_report_template.xml",
        "data/sequence_data.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/contracted_visits_views.xml",
        "views/contracted_company_views.xml",
        "views/menus.xml",
    ],
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'application': True,
}