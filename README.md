# Contracted Companies Visits with Document Management

An **Odoo 18** custom module for managing **contracted companies**, their **visits**, and related **documents** in a structured way.  
It extends Odoo’s capabilities by adding automatic folder creation, visit tracking, and PDF reporting.

---

## 🔑 Features

- **Company Management**
  - Store company details, contacts, and contracts.

- **Visit Management**
  - Schedule, track, and report on visits.
  - Auto-generate PDF visit reports.

- **Document Management**
  - Automatic folder structure per company.
  - Monthly folders by year for organized storage.
  - Support for multiple document types (reports, photos, certificates, contracts, etc.).
  - Upload and link documents directly to visits.

- **Reporting**
  - Statistics on visits and documents.

- **Integration**
  - Works seamlessly with Odoo Mail & Activities.

---

## 📂 Auto Folder Structure

Each company automatically gets a folder hierarchy like this:

Company Visits/
├── [Company Code] - [Company Name]/
│ ├── 2024/
│ │ ├── 01 - January/
│ │ ├── 02 - February/
│ │ └── ...
│ └── 2025/
│ ├── 01 - January/
│ └── ...


Visit reports and documents are saved in the appropriate monthly folder.

---

## ⚙️ Installation

1. Copy this module to your Odoo `addons` directory.
2. Update the app list:
   ```bash
   ./odoo-bin -u all -d <your_database>
3. Install Contracted Companies Visits from the Odoo Apps menu.


📝 Requirements

Odoo 18 Community or Enterprise

documents module installed

🚧 Roadmap

Advanced document search and tagging

Customizable visit workflows

KPI dashboard for visits & documents

