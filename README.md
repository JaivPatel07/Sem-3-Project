# EduSphere LMS

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey?logo=flask)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?logo=postgresql)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**EduSphere** is a premium, high-performance Learning Management System (LMS) designed to bridge the gap between students, educators, and administrators. Featuring a bespoke "Premium Light" design system, it delivers a modern, accessible, and highly-intuitive user experience.

---

## Table of Contents
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Security & Performance](#security--performance)

---

## Key Features

### Student Hub
- **Interactive Learning**: Industry-standard course player with sticky sidebars and chapter navigation.
- **Progress Tracking**: Real-time progress bars and "Continue where you left off" functionality.
- **Assessments**: Dynamic quiz system with instant grading and performance reports.
- **Certification**: Automated generation of PDF-styled completion certificates.

### Institute Workspace
- **Course Studio**: Drag-and-drop style creator for building multi-chapter modules.
- **Student Analytics**: Detailed tables showing enrollments, completion rates, and revenue.
- **Secure Onboarding**: Dedicated OTP-verified authentication flow for institutional safety.

### Admin Command Center
- **Unified Oversight**: Global metrics for users, courses, and active institutes.
- **Data Portability**: One-click CSV reporting for platform growth and audits.
- **User Management**: Granular control over accounts and course catalog sanitation.

---

## Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Python / Flask Framework |
| **Database** | PostgreSQL (Relational) |
| **Styling** | Vanilla CSS3 (Custom Design System) |
| **Frontend** | ES6+ JavaScript, Bootstrap 5.3 |
| **Security** | Werkzeug Security (HASH), Regex Validation |

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- PostgreSQL Server 14+

### Installation

1. **Clone the Repository**
2. **Environment Configuration**
   Copy `.env.example` to `.env` and configure your credentials.
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Initialize Database**
   ```bash
   python init_db.py  # Create schema
   python seed.py     # Load demonstration data
   ```
5. **Launch Application**
   ```bash
   python app.py
   ```

---

## Security & Performance

- **Thematic Integrity**: Optimized for 100% Light Theme consistency using a centralized CSS variable system.
- **Session Security**: Implements `HTTPOnly` and `SameSite` cookie policies with configurable secure flags.
- **Email Integrity**: Integrated SMTP layer for reliable OTP delivery and student performance reports.
- **Clean Architecture**: Orchestrated via a decoupled `python_db_methods` layer for robust data handling.
