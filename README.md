# EduTraker – Educational Management SaaS Platform

[![Status](https://img.shields.io/badge/Status-Active%20Development-green.svg)](https://github.com/MahmoudAlmodalal/EduTraker)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.1-orange.svg)](VERSION)

**EduTraker** is a comprehensive Software-as-a-Service (SaaS) educational management platform specifically designed to ensure academic continuity and administrative efficiency for institutions operating in **crisis-affected and low-connectivity environments**.

---

## 📖 Table of Contents

1.  [Project Overview](#-project-overview)
2.  [Key Features](#-key-features)
3.  [System Architecture](#-system-architecture)
4.  [User Roles & Permissions](#-user-roles--permissions)
5.  [Tech Stack](#-tech-stack)
6.  [Getting Started](#-getting-started)
7.  [Documentation](#-documentation)
8.  [Testing](#-testing)
9.  [License](#-license)

---

## 🌟 Project Overview

In regions affected by conflict or instability, educational continuity is often disrupted. EduTraker addresses this by providing a robust, **offline-first** platform that centralizes academic tracking, administrative tasks, and stakeholder communication.

### Core Objectives:
*   **Academic Continuity:** Mitigate the impact of disruptions on student learning.
*   **Administrative Efficiency:** Centralize management for schools and workstreams.
*   **Data-Driven Insights:** Enable humanitarian organizations to monitor performance trends.
*   **Resilience:** Support operations in areas with intermittent internet connectivity.

---

## ✨ Key Features

### 🏫 Multi-Tenant Management
*   **Hierarchical Structure:** Logical isolation between Workstreams and individual Schools.
*   **Cascading Configuration:** Global defaults with school-specific overrides (time zones, schedules).

### 📊 Academic Tracking
*   **Grade Management:** Weighted calculations for assignments, quizzes, and exams.
*   **Attendance Monitoring:** Real-time tracking with automated guardian notifications for absences.
*   **Knowledge Gap Analysis:** Identify specific areas where students need additional support.

### 📱 Offline-First Experience
*   **PWA Support:** Full functionality via Progressive Web App.
*   **Background Sync:** Automatic data synchronization when connectivity is restored.
*   **Local Caching:** Critical data stored locally using IndexedDB.

### 💬 Communication Hub
*   **Internal Messaging:** Secure 1-to-1 and group messaging for teachers, parents, and managers.
*   **Automated Notifications:** Push, email, and in-app alerts for grades and announcements.

---

## 🏗 System Architecture

EduTraker follows a modern **Three-Tier Architecture** designed for scalability and resilience:

1.  **Presentation Layer:** React-based PWA providing a responsive, accessible (WCAG 2.1 AA) interface.
2.  **Application Layer:** Django REST Framework (Python 3.9+) handling business logic and API versioning.
3.  **Data Layer:** 
    *   **MySQL 8:** Primary relational data storage.
    *   **Redis 6:** High-speed caching and session management.
    *   **Object Storage:** Secure storage for learning materials and reports.

---

## 👥 User Roles & Permissions

| Role | Scope | Primary Responsibilities |
| :--- | :--- | :--- |
| **Super Admin** | Global | System configuration, Workstream management, high-level analytics. |
| **WS Manager** | Workstream | Managing multiple schools, aggregated performance reporting. |
| **School Manager** | School | Staff management (Teachers/Secretaries), school-level analytics. |
| **Teacher** | Class | Lesson planning, grading, attendance, student communication. |
| **Secretary** | School | Student/Guardian registration and administrative support. |
| **Student** | Personal | Accessing learning materials, viewing grades and attendance. |
| **Guardian** | Linked Students | Monitoring child's progress, communicating with teachers. |

---

## 💻 Tech Stack

*   **Backend:** Python, Django, Django REST Framework
*   **Frontend:** React, Tailwind CSS, PWA (Service Workers)
*   **Database:** MySQL, Redis (Caching)
*   **Infrastructure:** Nginx, Gunicorn, Linux (Ubuntu LTS)
*   **Security:** JWT, TLS 1.2+, bcrypt (12+ rounds), AES-256

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.9+
*   Node.js 18+
*   MySQL 8.0+
*   Redis 6.0+

### Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/MahmoudAlmodalal/EduTraker.git
    cd EduTraker
    ```

2.  **Backend Setup:**
    ```bash
    cd backend
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
    ```

3.  **Frontend Setup:**
    ```bash
    cd frontend
    npm install
    npm start
    ```

---

## 📄 Documentation

For detailed specifications, please refer to the following documents:
*   [Software Requirements Specification (SRS)](EduTraker_SRS_Enhanced.md)
*   [API Documentation (Swagger/OpenAPI)](docs/api_spec.md)
*   [User Manual](docs/user_manual.md)

---

## 🧪 Testing

We maintain a high standard of quality with a target of **≥80% test coverage**.
*   **Unit Tests:** `pytest` for backend logic.
*   **Integration Tests:** Testing API endpoints and data flow.
*   **UAT:** Conducted in simulated low-bandwidth environments.

Run tests using:
```bash
pytest
npm test
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Developed with ❤️ by the EduTraker Team.*
