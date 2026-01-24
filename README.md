# EduTraker - Software Requirements Specification (SRS)

**Version:** 1.0  
**Date:** January 19, 2026  
**Project:** EduTraker - Educational Management SaaS Platform  
**Status:** Active Development

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [Functional Requirements](#3-functional-requirements)
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [User Roles and Permissions](#5-user-roles-and-permissions)
6. [System Architecture](#6-system-architecture)
7. [Data Model](#7-data-model)
8. [API Specifications](#8-api-specifications)
9. [User Stories and Scenarios](#9-user-stories-and-scenarios)
10. [Testing Requirements](#10-testing-requirements)
11. [Security Requirements](#11-security-requirements)
12. [Deployment and Infrastructure](#12-deployment-and-infrastructure)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document provides a comprehensive description of the EduTraker platform - a Software-as-a-Service (SaaS) educational management system designed specifically for institutions in crisis-affected regions. The document details all functional and non-functional requirements, system architecture, user roles, and technical specifications necessary for successful development and deployment.

### 1.2 Scope

**Product Name:** EduTraker  
**Product Type:** Multi-tenant SaaS Platform  
**Target Users:** Educational institutions in crisis-affected regions

**Key Objectives:**
- Ensure educational continuity during crises and disruptions
- Enhance administrative efficiency through centralized management
- Facilitate communication between stakeholders (teachers, students, guardians, administrators)
- Enable data-driven decision-making through comprehensive reporting and analytics
- Support offline functionality for areas with limited connectivity

**System Boundaries:**
- **In Scope:** User management, academic progress tracking, communication systems, reporting and analytics, content management, system configuration
- **Out of Scope:** Financial management, library management, transportation management, cafeteria services

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| SaaS | Software as a Service |
| RBAC | Role-Based Access Control |
| API | Application Programming Interface |
| PWA | Progressive Web App |
| JWT | JSON Web Token |
| TLS | Transport Layer Security |
| HTTPS | Hypertext Transfer Protocol Secure |
| MySQL | Relational Database Management System |
| Redis | In-memory data structure store (caching) |
| REST | Representational State Transfer |
| CRUD | Create, Read, Update, Delete |

### 1.4 References

- Django REST Framework Documentation: https://www.django-rest-framework.org/
- MySQL Documentation: https://dev.mysql.com/doc/
- React.js Documentation: https://react.dev/
- JWT Standard: RFC 7519

### 1.5 Document Conventions

- **Requirement IDs:** Follow the pattern `[Category]-[Subcategory]-[Number]`
  - Example: `FR-UM-001` (Functional Requirement - User Management - 001)
- **Priority Levels:** Critical, High, Medium, Low
- **Status Indicators:** Planned, In Progress, Implemented, Tested, Deployed

---

## 2. System Overview

### 2.1 Product Perspective

EduTraker is a standalone, cloud-based SaaS platform designed with a multi-tenant architecture. The system operates on a hierarchical organizational structure:

```
Admin (Super Admin)
  └── Workstream Manager
      └── School Manager
          ├── Teachers
          ├── Secretaries
          ├── Students
          └── Guardians
```

### 2.2 Product Features (High-Level)

1. **Multi-Tenant User Management** - Hierarchical user roles with granular permissions
2. **Academic Progress Tracking** - Grades, assignments, attendance, and skill assessment
3. **Communication Hub** - Messaging and notifications between all stakeholders
4. **Reporting & Analytics** - Performance insights at student, class, school, and workstream levels
5. **Content Management** - Lesson plans, learning materials, and resource sharing
6. **System Configuration** - Cascading settings from global to school-specific
7. **Offline Support** - PWA functionality for limited connectivity scenarios

### 2.3 User Characteristics

| User Role | Technical Expertise | Frequency of Use | Key Needs |
|-----------|---------------------|------------------|-----------|
| Admin | High | Daily | System oversight, user management, analytics |
| Workstream Manager | Medium-High | Daily | Multi-school management, aggregated reporting |
| School Manager | Medium | Daily | School operations, staff management, local reporting |
| Teacher | Low-Medium | Daily | Class management, grading, attendance, communication |
| Secretary | Low-Medium | Daily | Student registration, administrative support |
| Student | Low | Daily | View grades, assignments, attendance, content |
| Guardian | Low | Weekly | Monitor child's progress, communicate with teachers |

### 2.4 Operating Environment

**Client-Side:**
- Web browsers: Chrome, Firefox, Safari, Edge (latest 2 versions)
- Mobile devices: iOS 13+, Android 8+
- Progressive Web App (PWA) support required
- Offline storage capability (IndexedDB, Service Workers)

**Server-Side:**
- Operating System: Linux (Ubuntu 20.04 LTS or later)
- Python: 3.9+
- Django: 4.2+
- Django REST Framework: 3.14+
- Database: MySQL 8.0+
- Cache: Redis 6.0+
- Web Server: Nginx or Apache
- Application Server: Gunicorn or uWSGI
- Cloud Infrastructure: AWS, Azure, or GCP

### 2.5 Design and Implementation Constraints

1. **Technology Stack Constraints:**
   - Backend must use Django and Django REST Framework
   - Database must be MySQL for relational data
   - Frontend must be React-based PWA
   - Authentication must use JWT tokens

2. **Performance Constraints:**
   - Dashboard load time: ≤ 2 seconds for 95% of requests
   - Support for up to 10,000 concurrent users
   - API response time: ≤ 500ms for 90% of requests

3. **Security Constraints:**
   - All communications must use HTTPS (TLS 1.2+)
   - Passwords must be hashed using bcrypt (≥12 rounds)
   - Data encryption at rest for sensitive information
   - GDPR and data protection compliance

4. **Regulatory Constraints:**
   - Must comply with educational data privacy regulations
   - Must support data export for compliance purposes
   - Must maintain audit logs for critical operations

---

## 3. Functional Requirements

### 3.1 User Management (UM)

#### FR-UM-001: User Account Creation
**Priority:** Critical  
**Description:** The system shall allow authorized users to create accounts for users within their management scope.

**Detailed Requirements:**
- **FR-UM-001.1:** Super Admins can create Workstream Manager accounts
- **FR-UM-001.2:** Workstream Managers can create School Manager accounts for schools within their workstream
- **FR-UM-001.3:** School Managers can create Teacher and Secretary accounts for their school
- **FR-UM-001.4:** Secretaries can create Student and Guardian accounts

**Acceptance Criteria:**
- User creation form validates all required fields (email, full name, role)
- Email addresses must be unique across the system
- Temporary passwords are generated and sent securely
- New users appear in the appropriate user list immediately after creation
- Appropriate relationships are established (workstream, school linkage)

#### FR-UM-002: Role-Based Access Control (RBAC)
**Priority:** Critical  
**Description:** The system shall enforce role-based permissions ensuring users can only access functionalities and data relevant to their assigned role.

**Roles and Permissions Matrix:**

| Function | Admin | WS Manager | School Manager | Teacher | Secretary | Student | Guardian |
|----------|-------|------------|----------------|---------|-----------|---------|----------|
| Create Workstream Manager | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Create School Manager | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Create Teacher/Secretary | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Create Student/Guardian | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ |
| View System Analytics | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| View Workstream Reports | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| View School Reports | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Manage Grades | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| View Own Grades | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| View Child Grades | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |

**Acceptance Criteria:**
- Unauthorized access attempts return 403 Forbidden
- Users can only view/modify data within their scope (workstream/school)
- Permission checks occur at both API and UI levels

#### FR-UM-003: Student Registration
**Priority:** High  
**Description:** Secretaries shall be able to register new students with complete demographic and enrollment information.

**Required Student Information:**
- Full name
- Date of birth
- Gender
- National ID (if applicable)
- Enrollment date
- Grade/Class level
- Guardian linkage
- Contact information

**Acceptance Criteria:**
- All required fields must be completed before submission
- Students are automatically linked to the secretary's school
- Guardian linkage can be established during or after registration
- Registration confirmation is sent to linked guardians

#### FR-UM-004: Guardian Registration and Linkage
**Priority:** High  
**Description:** Secretaries shall be able to register guardians and link them to specific students.

**Detailed Requirements:**
- **FR-UM-004.1:** Guardians can be linked to multiple students
- **FR-UM-004.2:** Students can have multiple guardians
- **FR-UM-004.3:** Guardian relationship type must be specified (parent, legal guardian, etc.)

**Acceptance Criteria:**
- Guardian registration captures: full name, email, phone, relationship type
- System validates unique email addresses for guardians
- Guardians receive credentials and welcome email upon registration
- Guardians can immediately access linked student information

#### FR-UM-005: User Account Modification
**Priority:** High  
**Description:** Authorized users shall be able to update user account information.

**Modifiable Fields:**
- Full name
- Email (with verification)
- Role (within authorization scope)
- Active/Inactive status
- Workstream/School assignment

**Acceptance Criteria:**
- Changes to critical fields (email, role) require additional confirmation
- Audit log captures all modifications with timestamp and modifier identity
- Email changes trigger verification process
- Users are notified of significant changes to their accounts

#### FR-UM-006: User Account Deactivation/Activation
**Priority:** High  
**Description:** Authorized users shall be able to deactivate and reactivate user accounts.

**Detailed Requirements:**
- **FR-UM-006.1:** Deactivated users cannot log in
- **FR-UM-006.2:** Deactivation preserves historical data
- **FR-UM-006.3:** Reactivation restores full access
- **FR-UM-006.4:** Deactivation reason must be documented

**Acceptance Criteria:**
- Deactivated accounts display "Inactive" status
- Deactivated users' data remains accessible for reporting
- Reactivation can be performed by same authorization levels as deactivation
- System logs all activation/deactivation events

### 3.2 Academic Progress Tracking (APT)

#### FR-APT-001: Grade Management
**Priority:** Critical  
**Description:** Teachers shall be able to assign, modify, and manage student grades for assignments and exams.

**Grade Types:**
- Assignments
- Quizzes
- Midterm exams
- Final exams
- Projects
- Class participation

**Detailed Requirements:**
- **FR-APT-001.1:** Support for multiple grading scales (percentage, letter grades, points)
- **FR-APT-001.2:** Weighted grade calculation support
- **FR-APT-001.3:** Grade entry with optional comments/feedback
- **FR-APT-001.4:** Bulk grade import capability (CSV)

**Acceptance Criteria:**
- Grades are immediately visible to students and guardians upon entry
- Grade modifications create audit trail
- Invalid grade values are rejected with clear error messages
- Grade calculations are accurate for weighted categories

#### FR-APT-002: Knowledge Gap Identification
**Priority:** High  
**Description:** The system shall analyze student performance data to identify individual knowledge gaps.

**Analysis Criteria:**
- Performance below threshold (configurable per school)
- Declining performance trends
- Specific skill/topic weaknesses
- Comparative analysis with class average

**Acceptance Criteria:**
- System generates knowledge gap reports for teachers
- Recommendations for intervention are provided
- Historical tracking of knowledge gap remediation
- Parents are notified of significant gaps

#### FR-APT-003: Attendance Tracking
**Priority:** Critical  
**Description:** Teachers shall be able to record and track student attendance for their classes.

**Attendance Statuses:**
- Present
- Absent
- Late
- Excused absence
- Unexcused absence

**Detailed Requirements:**
- **FR-APT-003.1:** Daily attendance recording per class period
- **FR-APT-003.2:** Bulk attendance marking capability
- **FR-APT-003.3:** Attendance correction within configurable time window
- **FR-APT-003.4:** Automated absence notifications to guardians

**Acceptance Criteria:**
- Attendance can be marked within 24 hours of class session
- Attendance records are immediately visible to students and guardians
- System calculates attendance percentages automatically
- Teachers receive alerts for students with high absence rates

#### FR-APT-004: Student Dashboard
**Priority:** High  
**Description:** Students shall have access to a personalized dashboard displaying academic information.

**Dashboard Components:**
- Current grades by subject
- Upcoming assignments and deadlines
- Attendance summary
- Recent teacher feedback
- Academic progress charts
- Announcements

**Acceptance Criteria:**
- Dashboard loads within 2 seconds
- Real-time updates when new grades/assignments are posted
- Mobile-responsive design
- Accessible offline with cached data

#### FR-APT-005: Guardian Academic Monitoring
**Priority:** High  
**Description:** Guardians shall be able to monitor their child's academic progress including grades and assignments.

**Available Information:**
- All grades and assignments
- Attendance records
- Teacher comments and feedback
- Progress reports
- Comparative class performance (anonymized)

**Acceptance Criteria:**
- Guardians see same academic data as students
- Multi-child support (easy switching between children)
- Historical data access (full academic year)
- Export capability for records

### 3.3 Communication (COM)

#### FR-COM-001: Internal Messaging System
**Priority:** High  
**Description:** The system shall provide an internal messaging capability for communication between users.

**Message Types:**
- Direct messages (1-to-1)
- Group messages (class-wide, school-wide)
- Announcements (broadcast)

**Detailed Requirements:**
- **FR-COM-001.1:** Teachers can message students, guardians, and managers
- **FR-COM-001.2:** Guardians can message their child's teachers
- **FR-COM-001.3:** Managers can message all users within their scope
- **FR-COM-001.4:** Message threads and conversation history
- **FR-COM-001.5:** File attachment support (max 10MB per message)

**Acceptance Criteria:**
- Messages delivered within 5 seconds under normal load
- Read receipts available
- Message search functionality
- Notification of new messages (email and in-app)

#### FR-COM-002: Notification System
**Priority:** High  
**Description:** The system shall send automated notifications for important events and updates.

**Notification Triggers:**
- New grade posted
- Assignment due soon (24-hour reminder)
- Attendance marked absent
- New announcement
- Account changes
- System maintenance

**Notification Channels:**
- In-app notifications
- Email notifications
- SMS notifications (optional, future)
- Push notifications (PWA)

**Acceptance Criteria:**
- Users can configure notification preferences
- Notifications include actionable links
- Delivery confirmation for critical notifications
- Notification history accessible

#### FR-COM-003: Announcement Broadcasting
**Priority:** Medium  
**Description:** Administrators and managers shall be able to broadcast announcements to user groups.

**Target Groups:**
- All users (system-wide)
- Workstream-specific
- School-specific
- Class-specific
- Role-specific

**Acceptance Criteria:**
- Announcements appear prominently on recipient dashboards
- Acknowledgment tracking (read/unread)
- Scheduled announcement posting
- Announcement archiving

### 3.4 Reporting and Analytics (RA)

#### FR-RA-001: Student Performance Reports
**Priority:** High  
**Description:** The system shall generate comprehensive student performance reports.

**Report Types:**
- Individual student progress report
- Class performance summary
- Subject-specific analysis
- Attendance reports
- Knowledge gap reports
- Comparative analysis

**Report Formats:**
- PDF export
- Excel export
- CSV export
- Interactive dashboard

**Acceptance Criteria:**
- Reports generate within 30 seconds
- Historical data spanning full academic year
- Customizable date ranges
- Visual charts and graphs included

#### FR-RA-002: School-Level Analytics
**Priority:** High  
**Description:** School Managers shall be able to view aggregated analytics for their school.

**Available Metrics:**
- Overall student performance trends
- Teacher performance metrics
- Attendance statistics
- Grade distribution
- Department comparisons
- Year-over-year comparisons

**Acceptance Criteria:**
- Real-time data updates
- Drill-down capability to individual classes/students
- Exportable reports
- Customizable dashboards

#### FR-RA-003: Workstream-Level Analytics
**Priority:** High  
**Description:** Workstream Managers shall be able to view aggregated analytics across all schools in their workstream.

**Cross-School Metrics:**
- Comparative school performance
- Best practices identification
- Resource allocation insights
- Enrollment trends
- Staff performance across schools

**Acceptance Criteria:**
- Anonymized school comparisons
- Benchmark identification
- Data visualization with interactive charts
- Scheduled report generation

#### FR-RA-004: System Analytics
**Priority:** Medium  
**Description:** Super Admins shall have access to high-level system analytics.

**System Metrics:**
- Active user counts by role
- System performance metrics (response times, error rates)
- Usage patterns and trends
- Storage utilization
- API usage statistics

**Acceptance Criteria:**
- Real-time monitoring dashboard
- Historical trend analysis
- Alert thresholds for anomalies
- Export capability for external analysis

#### FR-RA-005: Staff Evaluation Reports
**Priority:** Medium  
**Description:** School Managers shall be able to conduct and view staff performance evaluations.

**Evaluation Criteria:**
- On-time grade submission
- Student performance outcomes
- Attendance recording compliance
- Parent communication frequency
- Professional development participation

**Acceptance Criteria:**
- Objective and subjective metrics combined
- Historical evaluation tracking
- Performance trend visualization
- Confidential storage and access

### 3.5 Content Management (CM)

#### FR-CM-001: Lesson Plan Creation
**Priority:** High  
**Description:** Teachers shall be able to create and manage lesson plans.

**Lesson Plan Components:**
- Learning objectives
- Topics covered
- Teaching methodology
- Resources needed
- Assessment methods
- Homework assignments
- Duration and scheduling

**Acceptance Criteria:**
- Template-based creation with customization
- Version history and revision tracking
- Sharing capability with other teachers
- Alignment with curriculum standards

#### FR-CM-002: Content Upload and Management
**Priority:** High  
**Description:** Teachers shall be able to upload and manage learning materials for students.

**Supported Content Types:**
- Documents (PDF, DOC, DOCX)
- Presentations (PPT, PPTX)
- Images (JPG, PNG, GIF)
- Videos (MP4, MOV) - stored externally
- Audio files (MP3, WAV)
- Links to external resources

**Content Organization:**
- Subject categorization
- Class/grade level assignment
- Topic tagging
- Search functionality

**Acceptance Criteria:**
- File size limit: 50MB per file
- Virus scanning on upload
- Preview capability for common formats
- Download tracking and analytics

#### FR-CM-003: Student Content Access
**Priority:** High  
**Description:** Students shall be able to access learning materials uploaded by their teachers.

**Access Features:**
- Browse by subject/class
- Search functionality
- Download capability
- Offline access (PWA caching)
- Recently accessed content

**Acceptance Criteria:**
- Content loads within 3 seconds
- Offline-first architecture for previously viewed content
- Mobile-optimized viewing
- Access tracking for teacher analytics

### 3.6 System Configuration (SC)

#### FR-SC-001: Cascading Configuration System
**Priority:** High  
**Description:** The system shall support hierarchical configuration settings from global to school-specific.

**Configuration Hierarchy:**
1. Global defaults (set by Super Admin)
2. Workstream-specific overrides
3. School-specific overrides

**Configurable Settings:**
- Academic calendar
- Grading scales and weights
- Attendance policies
- Notification preferences (defaults)
- Time zones
- Bell schedules
- Holiday calendars

**Acceptance Criteria:**
- Lower-level settings override higher-level defaults
- Clear indication of configuration source (global vs. local)
- Validation of configuration conflicts
- Configuration change history and rollback capability

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements

#### NFR-PERF-001: Response Time
**Priority:** Critical  
**Description:** The system shall maintain responsive performance under normal operating conditions.

**Performance Targets:**
- Dashboard page load: ≤ 2 seconds (95th percentile)
- API response time: ≤ 500ms (90th percentile)
- Search queries: ≤ 1 second (95th percentile)
- Report generation: ≤ 30 seconds for standard reports
- File uploads: Process within 5 seconds for files ≤ 10MB

**Measurement Criteria:**
- Measured under load of ≤ 10,000 concurrent users
- Network latency not included in measurements
- Client-side rendering time excluded

#### NFR-PERF-002: Scalability
**Priority:** High  
**Description:** The system shall scale to accommodate growth in users and data.

**Scalability Targets:**
- Support 10,000 concurrent users initially
- Scale to 50,000 concurrent users within 6 months
- Support 1 million student records
- Support 10,000 schools across multiple workstreams

**Scaling Approach:**
- Horizontal scaling for application servers
- Database read replicas for query performance
- CDN for static content delivery
- Auto-scaling based on load metrics

#### NFR-PERF-003: Caching Strategy
**Priority:** High  
**Description:** The system shall utilize caching to enhance performance.

**Caching Implementation:**
- Redis for session management
- Redis for frequently accessed data (user profiles, permissions)
- Browser caching for static assets (24-hour expiry)
- API response caching for read-heavy endpoints (5-minute TTL)
- PWA service worker caching for offline access

**Cache Invalidation:**
- Automatic invalidation on data updates
- Manual cache clearing capability for admins
- Cache warming for predictable access patterns

### 4.2 Security Requirements

#### NFR-SEC-001: Data Encryption
**Priority:** Critical  
**Description:** The system shall protect data through encryption in transit and at rest.

**Encryption Standards:**
- **In Transit:** HTTPS with TLS 1.2 or higher
- **At Rest:** AES-256 encryption for sensitive data
- **Database:** Encrypted columns for PII (Personally Identifiable Information)
- **Backups:** Encrypted backup storage

**Implementation:**
- SSL/TLS certificates from trusted CA
- Perfect Forward Secrecy (PFS) enabled
- HTTP Strict Transport Security (HSTS) headers
- Secure cookie attributes (HttpOnly, Secure, SameSite)

#### NFR-SEC-002: Password Security
**Priority:** Critical  
**Description:** The system shall securely store and manage user passwords.

**Password Requirements:**
- Minimum 8 characters
- Must contain: uppercase, lowercase, number, special character
- Password history: prevent reuse of last 5 passwords
- Password expiration: 90 days (configurable)

**Storage:**
- bcrypt hashing with ≥ 12 salt rounds
- No plaintext password storage
- No password transmission in URLs or logs

**Additional Security:**
- Account lockout after 5 failed login attempts
- Password reset via email with time-limited tokens
- Two-factor authentication (future enhancement)

#### NFR-SEC-003: Authentication and Authorization
**Priority:** Critical  
**Description:** The system shall implement secure authentication and authorization mechanisms.

**Authentication:**
- JWT (JSON Web Token) based authentication
- Access token expiration: 1 hour
- Refresh token expiration: 7 days
- Token refresh mechanism
- Secure token storage (httpOnly cookies for web)

**Authorization:**
- Role-based access control (RBAC)
- Permission checks at API and UI layers
- Least privilege principle
- Session management and timeout (30 minutes inactivity)

#### NFR-SEC-004: Data Privacy and Compliance
**Priority:** Critical  
**Description:** The system shall comply with data protection regulations.

**Privacy Measures:**
- GDPR compliance for EU users
- Data minimization principle
- Right to access personal data
- Right to data portability (export)
- Right to erasure (with retention policy exceptions)
- Consent management for data processing

**Audit and Compliance:**
- Comprehensive audit logging
- Data access tracking
- Regular security audits
- Privacy impact assessments
- Data breach notification procedures

#### NFR-SEC-005: Input Validation and Sanitization
**Priority:** High  
**Description:** The system shall validate and sanitize all user inputs to prevent security vulnerabilities.

**Protection Against:**
- SQL injection
- Cross-Site Scripting (XSS)
- Cross-Site Request Forgery (CSRF)
- Command injection
- Path traversal

**Implementation:**
- Input validation on client and server sides
- Parameterized queries for database access
- Output encoding for all user-generated content
- CSRF tokens for state-changing operations
- Content Security Policy (CSP) headers

### 4.3 Reliability Requirements

#### NFR-REL-001: System Uptime
**Priority:** Critical  
**Description:** The system shall maintain high availability.

**Uptime Target:** ≥ 99% per calendar month (excluding scheduled maintenance)

**Calculation:**
- Planned downtime excludes maintenance windows (announced 48 hours in advance)
- Maximum planned downtime: 4 hours per month
- Maximum unplanned downtime: 3.6 hours per month

**High Availability Measures:**
- Redundant application servers
- Database replication (master-slave)
- Load balancing
- Failover mechanisms
- Health monitoring and auto-recovery

#### NFR-REL-002: Offline Functionality (PWA)
**Priority:** High  
**Description:** The Progressive Web App shall support offline functionality.

**Offline Capabilities:**
- View previously loaded dashboards
- Access cached learning materials
- Queue actions for later sync (grade entry, messages)
- Offline notification banner
- Background sync when connection restored

**Data Synchronization:**
- Automatic sync on connection restoration
- Conflict resolution for concurrent edits
- Sync status indicators
- Manual sync trigger option

**Cached Data:**
- User profile and preferences
- Recent grades and assignments
- Attendance records (last 30 days)
- Learning materials (last accessed)
- Messages (last 50 conversations)

#### NFR-REL-003: Data Backup and Recovery
**Priority:** Critical  
**Description:** The system shall maintain regular backups for disaster recovery.

**Backup Schedule:**
- Full database backup: Daily at 2:00 AM UTC
- Incremental backups: Every 6 hours
- File storage backup: Daily
- Backup retention: 30 days

**Recovery Objectives:**
- Recovery Point Objective (RPO): ≤ 6 hours
- Recovery Time Objective (RTO): ≤ 4 hours
- Tested recovery procedures: Monthly

**Backup Storage:**
- Encrypted backup storage
- Geographically distributed backup locations
- Automated backup verification

#### NFR-REL-004: Error Handling
**Priority:** High  
**Description:** The system shall gracefully handle errors and provide meaningful feedback.

**Error Handling:**
- User-friendly error messages (no stack traces to users)
- Detailed error logging for administrators
- Automatic error reporting to monitoring system
- Fallback mechanisms for critical functions

**Error Recovery:**
- Graceful degradation for non-critical features
- Retry mechanisms for transient failures
- User guidance for recoverable errors
- Contact support for unrecoverable errors

### 4.4 Usability Requirements

#### NFR-USAB-001: User Interface Design
**Priority:** High  
**Description:** The system shall provide an intuitive and user-friendly interface.

**Design Principles:**
- Simple, clean layout
- Consistent navigation across all pages
- Clear visual hierarchy
- Responsive design (mobile, tablet, desktop)
- Minimal clicks to common tasks (≤ 3 clicks)

**UI Framework:**
- React-based frontend
- Material-UI or similar component library
- Accessibility-first design
- Progressive disclosure of complex features

**User Experience:**
- Contextual help and tooltips
- Clear action buttons and labels
- Visual feedback for user actions
- Loading indicators for async operations

#### NFR-USAB-002: Accessibility
**Priority:** High  
**Description:** The system shall be accessible to users with disabilities.

**Accessibility Standards:**
- WCAG 2.1 Level AA compliance
- Keyboard navigation support
- Screen reader compatibility
- Sufficient color contrast (4.5:1 minimum)
- Resizable text (up to 200%)
- Alternative text for images

**Assistive Technology Support:**
- ARIA labels and landmarks
- Focus indicators
- Skip navigation links
- Semantic HTML structure

#### NFR-USAB-003: Multi-Language Support
**Priority:** Medium  
**Description:** The system shall support multiple languages (future phase).

**Initial Language:** English  
**Planned Languages:** Arabic, French, Spanish

**Internationalization (i18n):**
- Externalized text strings
- Right-to-left (RTL) layout support
- Date and time localization
- Number formatting localization
- Currency formatting (if applicable)

#### NFR-USAB-004: User Onboarding
**Priority:** Medium  
**Description:** The system shall provide effective onboarding for new users.

**Onboarding Features:**
- Role-specific welcome screens
- Interactive tutorial for first-time users
- Guided tours for key features
- Help documentation and FAQs
- Video tutorials (future)

**Learning Resources:**
- Contextual help throughout the application
- Searchable knowledge base
- User guides per role
- In-app support chat (future)

### 4.5 Maintainability Requirements

#### NFR-MAINT-002: System Architecture
**Priority:** High  
**Description:** The system shall follow a layered architecture pattern for maintainability.

**Architecture Layers:**
1. **Presentation Layer:** React PWA frontend
2. **API Layer:** Django REST Framework
3. **Business Logic Layer:** Django models and services
4. **Data Access Layer:** Django ORM
5. **Data Layer:** MySQL database + Redis cache

**Design Patterns:**
- Model-View-Controller (MVC) in Django
- RESTful API design
- Service-oriented architecture
- Repository pattern for data access

**Modularity:**
- Separate Django apps for each major feature (accounts, student, teacher, etc.)
- Loosely coupled components
- Clear module boundaries
- Dependency injection where appropriate

#### NFR-MAINT-003: Documentation
**Priority:** High  
**Description:** The system shall maintain comprehensive documentation.

**Required Documentation:**
- API documentation (OpenAPI/Swagger)
- Database schema documentation
- Deployment guides
- User manuals (per role)
- Administrator guides
- Developer onboarding guide
- Architecture decision records (ADRs)

**Documentation Standards:**
- Up-to-date with code changes
- Version controlled alongside code
- Searchable and well-organized
- Include examples and diagrams

#### NFR-MAINT-004: Logging and Monitoring
**Priority:** High  
**Description:** The system shall implement comprehensive logging and monitoring.

**Logging Requirements:**
- Application logs (INFO, WARNING, ERROR, CRITICAL)
- Access logs (all API requests)
- Audit logs (sensitive operations)
- Performance logs (slow queries, high resource usage)
- Security logs (authentication failures, permission denials)

**Log Management:**
- Centralized log aggregation
- Log retention: 90 days for application logs, 1 year for audit logs
- Log analysis and search capabilities
- Automated alerting for critical errors

**Monitoring:**
- Real-time system health dashboard
- Performance metrics (CPU, memory, disk, network)
- Application metrics (request rates, error rates, response times)
- Database metrics (query performance, connection pool)
- Alerting thresholds for anomalies

### 4.6 Data Requirements

#### NFR-DATA-001: Data Storage
**Priority:** Critical  
**Description:** The system shall use appropriate storage technologies for different data types.

**Primary Database:** MySQL 8.0+
- User accounts and profiles
- Academic data (grades, attendance)
- School and workstream structure
- System configuration
- Relationships and references

**Cache Storage:** Redis 6.0+
- Session data
- Frequently accessed user data
- API response caching
- Rate limiting counters

**Cloud Storage:** AWS S3, Azure Blob, or Google Cloud Storage
- Learning materials and documents
- Report files
- User uploaded content
- System backups
- Media files (images, videos)

**Client Storage (PWA):**
- IndexedDB for offline data
- Service worker cache for assets
- LocalStorage for preferences

#### NFR-DATA-002: Data Retention
**Priority:** High  
**Description:** The system shall maintain data retention policies.

**Retention Periods:**
- Active student records: Indefinite (while enrolled)
- Graduated/transferred student records: 7 years
- User activity logs: 90 days
- Audit logs: 7 years
- System logs: 90 days
- Backups: 30 days

**Data Archival:**
- Automated archival of old records
- Compressed archive storage
- Searchable archives for compliance
- Data retrieval procedures

#### NFR-DATA-003: Data Integrity
**Priority:** Critical  
**Description:** The system shall maintain data accuracy and consistency.

**Integrity Measures:**
- Database constraints (foreign keys, unique constraints, check constraints)
- Transaction management (ACID compliance)
- Input validation at all layers
- Referential integrity enforcement
- Data type validation

**Consistency:**
- Eventual consistency for cached data (5-minute maximum staleness)
- Strong consistency for critical operations (grade entry, attendance)
- Conflict resolution for offline sync
- Data validation on sync

---

## 5. User Roles and Permissions

### 5.1 Role Definitions

#### 5.1.1 Super Admin
**Description:** System administrator with full access across all workstreams and schools.

**Primary Responsibilities:**
- System-wide configuration and maintenance
- Workstream Manager account management
- High-level system analytics and monitoring
- Security and access control oversight
- System updates and maintenance

**Key Permissions:**
- Create/modify/delete Workstream Managers
- Access all workstreams and schools
- View system-wide analytics
- Modify global system configurations
- Access audit logs and security reports
- Manage system users and roles

**Restrictions:**
- Cannot directly manage individual schools (must delegate to managers)
- Cannot access student-specific academic data without school manager approval

#### 5.1.2 Workstream Manager
**Description:** Manages a collection of schools within a geographical or organizational workstream.

**Primary Responsibilities:**
- School entity creation and management
- School Manager assignment and oversight
- Cross-school performance analysis
- Resource allocation across schools
- Workstream-level reporting

**Key Permissions:**
- Create/modify schools within their workstream
- Create/modify/delete School Managers
- View aggregated reports across all schools in workstream
- Configure workstream-level settings
- Access school-level data within their workstream
- Communicate with all users in their workstream

**Restrictions:**
- Cannot access schools outside their workstream
- Cannot create other Workstream Managers
- Cannot modify global system settings
- Cannot directly manage teachers or students

#### 5.1.3 School Manager
**Description:** Manages a single school, overseeing all academic and administrative operations.

**Primary Responsibilities:**
- Teacher and Secretary account management
- School-level performance monitoring
- Staff evaluation and professional development
- School-specific configuration
- Departmental oversight

**Key Permissions:**
- Create/modify/delete Teachers and Secretaries for their school
- View all school-level reports and analytics
- Conduct staff evaluations
- Configure school-specific settings
- Monitor all classes and students in their school
- Communicate with all school users
- Generate school reports

**Restrictions:**
- Cannot access other schools' data
- Cannot create School Managers
- Cannot modify workstream or global settings
- Cannot directly modify student grades (view only)

#### 5.1.4 Teacher
**Description:** Manages courses, delivers instruction, and assesses student performance.

**Primary Responsibilities:**
- Lesson planning and curriculum delivery
- Student attendance recording
- Grading and assessment
- Student progress monitoring
- Parent/guardian communication
- Content and resource management

**Key Permissions:**
- Create/modify lesson plans for assigned courses
- Record attendance for assigned classes
- Enter/modify grades for assigned students
- Upload learning materials and resources
- View student academic records (assigned students only)
- Communicate with students, guardians, and managers
- Generate class performance reports

**Restrictions:**
- Cannot access students not assigned to them
- Cannot modify school or system settings
- Cannot create user accounts
- Cannot access other teachers' grade books
- Cannot modify finalized/locked grades (if grade locking enabled)

#### 5.1.5 Secretary
**Description:** Provides administrative support, primarily focused on student and guardian registration.

**Primary Responsibilities:**
- Student registration and enrollment
- Guardian account creation and linking
- Administrative report generation
- Record maintenance and updates
- Communication support

**Key Permissions:**
- Create/modify student accounts
- Create/modify guardian accounts
- Link guardians to students
- Update student demographic information
- Generate administrative reports (enrollment lists, contact information)
- View school-level student information
- Assist with scheduling and administrative tasks

**Restrictions:**
- Cannot modify grades or academic content
- Cannot create teacher or manager accounts
- Cannot access detailed academic performance data
- Cannot modify school settings
- View-only access to attendance and grades

#### 5.1.6 Student
**Description:** Enrolled learner accessing academic information and learning resources.

**Primary Responsibilities:**
- Accessing learning materials
- Completing assignments
- Monitoring own academic progress
- Communicating with teachers (when appropriate)

**Key Permissions:**
- View own grades and assignments
- Access own attendance records
- Download/view learning materials for enrolled courses
- View teacher feedback and comments
- Access personalized dashboard
- Receive notifications about assignments and grades
- View class schedule and announcements

**Restrictions:**
- Cannot view other students' information
- Cannot modify any data (except personal profile)
- Cannot access administrative functions
- Cannot communicate with other students directly (future feature)
- Cannot view teacher or school management data

#### 5.1.7 Guardian
**Description:** Parent or legal guardian monitoring child's educational progress.

**Primary Responsibilities:**
- Monitoring child's academic performance
- Communication with teachers
- Supporting child's learning
- Staying informed about school activities

**Key Permissions:**
- View linked child's grades and assignments
- View linked child's attendance records
- Access linked child's learning materials
- Communicate with child's teachers
- Receive notifications about child's academic status
- View child's schedule and announcements
- Access progress reports and analytics

**Restrictions:**
- Cannot view other students' information
- Cannot modify any academic data
- Cannot access school administrative functions
- Cannot communicate with students directly
- Limited to linked children only (no broader access)

#### 5.1.8 Guest
**Description:** Unauthenticated user with minimal system access.

**Primary Responsibilities:**
- None (informational access only)

**Key Permissions:**
- View public information (school contact info, if enabled)
- Access login and registration pages
- View general system information

**Restrictions:**
- Cannot access any user-specific data
- Cannot access academic information
- Cannot perform any system actions
- Must authenticate to gain additional permissions

### 5.2 Permission Matrix

**Legend:**
- ✓ = Full Access
- R = Read Only
- ✗ = No Access
- C = Create Only
- M = Modify Only

| Resource/Action | Admin | WS Mgr | School Mgr | Teacher | Secretary | Student | Guardian | Guest |
|----------------|-------|---------|-------------|---------|-----------|---------|----------|-------|
| **User Management** |
| Create Workstream Manager | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Create School Manager | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Create Teacher/Secretary | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Create Student | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Create Guardian | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Deactivate Users | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Academic Management** |
| Manage Grades | ✗ | ✗ | R | ✓ | ✗ | ✗ | ✗ | ✗ |
| View Own Grades | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| View Child Grades | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Record Attendance | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| View Attendance (Own) | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| View Attendance (Child) | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Create Lesson Plans | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Upload Content | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Access Learning Materials | ✗ | ✗ | R | R | R | ✓ | ✓ | ✗ |
| **Reporting & Analytics** |
| System Analytics | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Workstream Reports | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| School Reports | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Class Reports | ✗ | R | R | ✓ | ✗ | ✗ | ✗ | ✗ |
| Student Reports | ✗ | R | R | R | R | ✓ | ✓ | ✗ |
| Staff Evaluations | ✗ | R | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Communication** |
| System Announcements | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Workstream Announcements | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| School Announcements | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Message Teachers | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Message Guardians | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Message Students | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| **Configuration** |
| Global Settings | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Workstream Settings | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| School Settings | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Personal Preferences | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |

---

## 6. System Architecture

### 6.1 Architecture Overview

EduTraker follows a three-tier architecture pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌──────────────────────┐      ┌──────────────────────┐    │
│  │   Web Application    │      │   Mobile PWA         │    │
│  │   (React.js)         │      │   (React.js)         │    │
│  └──────────────────────┘      └──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTPS/REST
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Django REST Framework API                     │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │   Auth &   │  │  Academic  │  │   Report   │     │  │
│  │  │ Permission │  │  Progress  │  │ Analytics  │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘     │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │   User     │  │Communication│  │  Content   │     │  │
│  │  │Management  │  │   System   │  │ Management │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    MySQL     │  │     Redis    │  │ Cloud Storage│      │
│  │  (Primary DB)│  │   (Cache)    │  │  (S3/Azure)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Component Breakdown

#### 6.2.1 Presentation Layer Components

**Web Application (React PWA):**
- **Technology:** React 18+, React Router, Material-UI
- **State Management:** Redux or Context API
- **Build Tool:** Vite or Create React App
- **Features:**
  - Responsive design (mobile-first)
  - Service workers for offline capability
  - Progressive enhancement
  - Code splitting for performance
  - Lazy loading of routes

**Key React Modules:**
- Authentication module (login, registration, password reset)
- Dashboard module (role-specific)
- User management module
- Academic tracking module (grades, attendance)
- Communication module (messaging, notifications)
- Reporting module (charts, exports)
- Content viewer module

#### 6.2.2 Application Layer Components

**Django Applications Structure:**

```
eduTrack/ (project root)
├── accounts/          # User authentication and management
│   ├── models.py      # CustomUser, SystemConfiguration
│   ├── serializers.py # User serializers
│   ├── views/         # Auth views, user CRUD
│   ├── permissions.py # Role-based permissions
│   └── urls.py        # Account endpoints
├── workstream/        # Workstream management
│   ├── models.py      # WorkStream model
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── school/            # School entity management
│   ├── models.py      # School, AcademicYear, ClassRoom
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── student/           # Student-specific functionality
│   ├── models.py      # Student profile, enrollments
│   ├── views.py       # Student dashboard, grades view
│   └── urls.py
├── teacher/           # Teacher-specific functionality
│   ├── models.py      # Teacher profile, assignments
│   ├── views.py       # Lesson plans, grading, attendance
│   └── urls.py
├── guardian/          # Guardian-specific functionality
│   ├── models.py      # Guardian profile, relationships
│   ├── views.py       # Child monitoring views
│   └── urls.py
├── secretary/         # Secretary administrative functions
│   ├── views.py       # Registration views
│   └── urls.py
├── manager/           # Manager dashboards and reports
│   ├── views.py       # Analytics, evaluations
│   └── urls.py
├── reports/           # Reporting and analytics engine
│   ├── services.py    # Report generation logic
│   ├── views.py       # Report APIs
│   └── exporters.py   # PDF, Excel exporters
├── notifications/     # Notification system
│   ├── models.py      # Notification, UserNotification
│   ├── services.py    # Notification delivery
│   └── tasks.py       # Celery tasks
└── user_messages/     # Internal messaging system
    ├── models.py      # Message, Thread
    ├── views.py       # Messaging APIs
    └── urls.py
```

**Core Services:**

1. **Authentication Service:**
   - JWT token generation and validation
   - Password hashing and verification
   - Session management
   - Role-based permission checking

2. **Academic Service:**
   - Grade calculation and management
   - Attendance tracking and analysis
   - Progress assessment
   - Knowledge gap identification

3. **Reporting Service:**
   - Data aggregation
   - Report generation (PDF, Excel, CSV)
   - Chart data preparation
   - Scheduled report generation

4. **Notification Service:**
   - Event-based notification triggers
   - Multi-channel delivery (email, in-app, push)
   - Notification preferences management
   - Delivery tracking

5. **Content Service:**
   - File upload and validation
   - Cloud storage integration
   - Content organization and tagging
   - Access control

#### 6.2.3 Data Layer Components

**MySQL Database:**
- **Version:** 8.0+
- **Purpose:** Primary relational data storage
- **Configuration:**
  - InnoDB storage engine
  - UTF-8mb4 character set
  - Connection pooling
  - Read replicas for scalability

**Key Tables:**
- users (CustomUser model)
- workstreams
- schools
- students
- teachers
- guardians
- courses
- classrooms
- grades
- attendance
- assignments
- messages
- notifications
- system_configurations

**Redis Cache:**
- **Version:** 6.0+
- **Purpose:** Session management, data caching, rate limiting
- **Cached Data:**
  - User sessions
  - Permission lookups
  - Frequently accessed profiles
  - API response caching
  - Rate limiting counters

**Cloud Storage:**
- **Provider:** AWS S3 / Azure Blob / Google Cloud Storage
- **Purpose:** Unstructured data and large files
- **Content:**
  - Learning materials (PDFs, videos, images)
  - Generated reports
  - User uploads
  - System backups

### 6.3 Data Flow Diagrams

#### 6.3.1 User Authentication Flow

```
User → Login Form → API (POST /auth/login/)
                    ↓
              Validate Credentials
                    ↓
              Generate JWT Tokens
                    ↓
         Return {access_token, refresh_token}
                    ↓
    Store tokens in httpOnly cookies/localStorage
                    ↓
        Subsequent requests include access_token
                    ↓
         API validates token on each request
                    ↓
          Token expired? → Refresh using refresh_token
                    ↓
              Process request
```

#### 6.3.2 Grade Entry Flow

```
Teacher → Grade Entry Form → API (POST /grades/)
                               ↓
                    Check Permission (IsTeacher)
                               ↓
                    Validate Student Assignment
                               ↓
                    Save Grade to Database
                               ↓
                    Invalidate Cache (student grades)
                               ↓
                    Trigger Notification (student, guardian)
                               ↓
                    Return Success Response
                               ↓
           Update UI → Student/Guardian Dashboards Updated
```

#### 6.3.3 Report Generation Flow

```
Manager → Request Report → API (POST /reports/generate/)
                            ↓
                Check Permission (IsManager)
                            ↓
                Query Database (filtered by scope)
                            ↓
                Aggregate Data
                            ↓
                Generate Charts/Graphs
                            ↓
                Format Report (PDF/Excel)
                            ↓
                Upload to Cloud Storage
                            ↓
                Return Download URL
                            ↓
        Manager Downloads/Views Report
```

### 6.4 Security Architecture

**Security Layers:**

1. **Network Security:**
   - HTTPS/TLS encryption
   - Firewall rules
   - DDoS protection
   - Rate limiting

2. **Application Security:**
   - Input validation
   - Output encoding
   - CSRF protection
   - XSS prevention
   - SQL injection prevention

3. **Authentication & Authorization:**
   - JWT-based authentication
   - Role-based access control (RBAC)
   - Permission decorators on API views
   - Session management

4. **Data Security:**
   - Password hashing (bcrypt)
   - Encrypted sensitive data
   - Secure file uploads
   - Data access auditing

**Security Implementation:**

```python
# Permission checking at API level
class GradeCreateAPI(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    
    def post(self, request):
        # Additional business logic validation
        student_id = request.data.get('student_id')
        if not self.can_grade_student(request.user, student_id):
            return Response(
                {"error": "You don't have permission to grade this student"},
                status=403
            )
        # Process grade entry
        ...
```

---

## 7. Data Model

### 7.1 Entity Relationship Diagram (ERD)

```
┌──────────────┐          ┌──────────────┐
│  WorkStream  │1       N │    School    │
│              │─────────>│              │
└──────────────┘          └──────────────┘
                                 │1
                                 │
                                 │N
                          ┌──────────────┐
                          │ CustomUser   │
                          │ (Base)       │
                          └──────────────┘
                                 │
                 ┌───────────────┼───────────────┬───────────┐
                 │               │               │           │
          ┌──────────┐    ┌──────────┐   ┌──────────┐ ┌──────────┐
          │ Student  │    │ Teacher  │   │ Guardian │ │Secretary │
          └──────────┘    └──────────┘   └──────────┘ └──────────┘
                 │               │               │
                 │               │               │
          ┌──────────┐    ┌──────────┐   ┌──────────────┐
          │  Grade   │    │LessonPlan│   │StudentGuardian│
          └──────────┘    └──────────┘   │(Link Table)  │
                 │               │        └──────────────┘
                 │               │
          ┌──────────┐    ┌──────────┐
          │Attendance│    │Assignment│
          └──────────┘    └──────────┘
```

### 7.2 Core Models

#### 7.2.1 CustomUser Model

```python
class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Central user model for all system users"""
    # Primary fields
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    
    # Organizational relationships
    work_stream = models.ForeignKey('WorkStream', null=True, blank=True)
    school = models.ForeignKey('School', null=True, blank=True)
    
    # Authentication fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Audit fields
    created_by = models.ForeignKey('self', null=True, related_name='created_users')
    modified_at = models.DateTimeField(auto_now=True)
```

**Indexes:**
- email (unique)
- role
- (work_stream, school) - composite for filtering

**Constraints:**
- Email uniqueness
- Role must be valid choice
- School must belong to work_stream if both are set

#### 7.2.2 WorkStream Model

```python
class WorkStream(models.Model):
    """Collection of schools under common management"""
    workstream_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    capacity = models.IntegerField(help_text="Maximum number of schools")
    manager = models.OneToOneField(CustomUser, related_name='managed_workstream')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
```

#### 7.2.3 School Model

```python
class School(models.Model):
    """Individual educational institution"""
    school_name = models.CharField(max_length=200)
    workstream = models.ForeignKey(WorkStream, related_name='schools')
    location = models.CharField(max_length=300)
    capacity = models.IntegerField(help_text="Maximum number of students")
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    
    # Operational status
    is_active = models.BooleanField(default=True)
    academic_year_start = models.DateField()
    academic_year_end = models.DateField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
```

#### 7.2.4 Student Profile Model

```python
class StudentProfile(models.Model):
    """Extended profile for student users"""
    user = models.OneToOneField(CustomUser, related_name='student_profile')
    student_id = models.CharField(max_length=50, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    grade_level = models.IntegerField()
    enrollment_date = models.DateField()
    
    # Academic tracking
    current_gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    total_absences = models.IntegerField(default=0)
    
    # Personal information
    national_id = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100)
    
    # Status
    enrollment_status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('graduated', 'Graduated'),
                 ('transferred', 'Transferred'), ('withdrawn', 'Withdrawn')]
    )
```

#### 7.2.5 Guardian-Student Relationship

```python
class StudentGuardian(models.Model):
    """Links guardians to students"""
    student = models.ForeignKey(CustomUser, related_name='guardians')
    guardian = models.ForeignKey(CustomUser, related_name='students')
    relationship_type = models.CharField(
        max_length=50,
        choices=[('parent', 'Parent'), ('legal_guardian', 'Legal Guardian'),
                 ('foster_parent', 'Foster Parent'), ('other', 'Other')]
    )
    is_primary = models.BooleanField(default=False)
    can_pickup = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'guardian']
```

#### 7.2.6 Course and Classroom Models

```python
class Course(models.Model):
    """Academic course/subject"""
    course_name = models.CharField(max_length=200)
    course_code = models.CharField(max_length=50, unique=True)
    school = models.ForeignKey(School, related_name='courses')
    description = models.TextField()
    grade_level = models.IntegerField()
    credits = models.DecimalField(max_digits=3, decimal_places=1)
    is_active = models.BooleanField(default=True)

class ClassRoom(models.Model):
    """Specific class instance of a course"""
    course = models.ForeignKey(Course, related_name='classes')
    teacher = models.ForeignKey(CustomUser, related_name='taught_classes')
    academic_year = models.ForeignKey('AcademicYear', related_name='classes')
    section = models.CharField(max_length=10)  # e.g., "A", "B"
    schedule = models.JSONField()  # {day: time} mapping
    max_students = models.IntegerField()
    
    class Meta:
        unique_together = ['course', 'teacher', 'academic_year', 'section']
```

#### 7.2.7 Grade Model

```python
class Grade(models.Model):
    """Individual grade entry"""
    student = models.ForeignKey(CustomUser, related_name='grades')
    classroom = models.ForeignKey(ClassRoom, related_name='grades')
    assignment = models.ForeignKey('Assignment', related_name='grades')
    
    # Grade information
    score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    letter_grade = models.CharField(max_length=2, blank=True)
    
    # Metadata
    graded_by = models.ForeignKey(CustomUser, related_name='graded_assignments')
    graded_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    teacher_comments = models.TextField(blank=True)
    is_final = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['student', 'assignment']
        indexes = [
            models.Index(fields=['student', 'classroom']),
            models.Index(fields=['graded_at']),
        ]
```

#### 7.2.8 Attendance Model

```python
class Attendance(models.Model):
    """Daily attendance record"""
    student = models.ForeignKey(CustomUser, related_name='attendance_records')
    classroom = models.ForeignKey(ClassRoom, related_name='attendance_records')
    date = models.DateField()
    
    # Attendance status
    status = models.CharField(
        max_length=20,
        choices=[
            ('present', 'Present'),
            ('absent', 'Absent'),
            ('late', 'Late'),
            ('excused', 'Excused Absence'),
            ('unexcused', 'Unexcused Absence'),
        ]
    )
    
    # Timing
    check_in_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Metadata
    recorded_by = models.ForeignKey(CustomUser, related_name='recorded_attendance')
    recorded_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'classroom', 'date']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['classroom', 'date']),
        ]
```

#### 7.2.9 Assignment Model

```python
class Assignment(models.Model):
    """Course assignment or assessment"""
    classroom = models.ForeignKey(ClassRoom, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Assignment details
    assignment_type = models.CharField(
        max_length=50,
        choices=[
            ('homework', 'Homework'),
            ('quiz', 'Quiz'),
            ('exam', 'Exam'),
            ('project', 'Project'),
            ('participation', 'Class Participation'),
        ]
    )
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    weight = models.DecimalField(max_digits=4, decimal_places=2)  # For weighted grades
    
    # Dates
    assigned_date = models.DateField()
    due_date = models.DateField()
    
    # Resources
    instructions_url = models.URLField(blank=True)
    attachments = models.JSONField(default=list)  # List of file URLs
    
    # Metadata
    created_by = models.ForeignKey(CustomUser, related_name='created_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
```

#### 7.2.10 Notification Model

```python
class Notification(models.Model):
    """System notifications"""
    recipient = models.ForeignKey(CustomUser, related_name='notifications')
    
    # Notification content
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('grade_posted', 'Grade Posted'),
            ('assignment_due', 'Assignment Due Soon'),
            ('attendance_marked', 'Attendance Marked'),
            ('announcement', 'Announcement'),
            ('message_received', 'Message Received'),
            ('system', 'System Notification'),
        ]
    )
    
    # Links and actions
    action_url = models.CharField(max_length=500, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.IntegerField(null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Delivery tracking
    email_sent = models.BooleanField(default=False)
    push_sent = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
        ]
```

#### 7.2.11 Message Model

```python
class Message(models.Model):
    """Internal messaging system"""
    sender = models.ForeignKey(CustomUser, related_name='sent_messages')
    recipients = models.ManyToManyField(CustomUser, related_name='received_messages')
    
    # Message content
    subject = models.CharField(max_length=200)
    body = models.TextField()
    attachments = models.JSONField(default=list)
    
    # Threading
    parent_message = models.ForeignKey('self', null=True, blank=True, related_name='replies')
    thread_id = models.UUIDField(db_index=True)
    
    # Metadata
    sent_at = models.DateTimeField(auto_now_add=True)
    is_draft = models.BooleanField(default=False)
    
class MessageReceipt(models.Model):
    """Tracks message read status per recipient"""
    message = models.ForeignKey(Message, related_name='receipts')
    recipient = models.ForeignKey(CustomUser, related_name='message_receipts')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
```

### 7.3 Database Indexes and Optimization

**Critical Indexes:**
```sql
-- User lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_school ON users(school_id);
CREATE INDEX idx_users_workstream ON users(work_stream_id);

-- Academic data
CREATE INDEX idx_grades_student_classroom ON grades(student_id, classroom_id);
CREATE INDEX idx_attendance_student_date ON attendance(student_id, date);
CREATE INDEX idx_attendance_classroom_date ON attendance(classroom_id, date);

-- Communication
CREATE INDEX idx_notifications_recipient_unread ON notifications(recipient_id, is_read, created_at);
CREATE INDEX idx_messages_thread ON messages(thread_id, sent_at);

-- Composite indexes for common queries
CREATE INDEX idx_users_school_role ON users(school_id, role);
CREATE INDEX idx_grades_classroom_date ON grades(classroom_id, graded_at);
```

**Query Optimization Strategies:**
1. Use select_related() for foreign key joins
2. Use prefetch_related() for many-to-many and reverse foreign keys
3. Implement database-level pagination
4. Use aggregation queries for reporting
5. Cache frequently accessed data in Redis

---

## 8. API Specifications

### 8.1 API Design Principles

**RESTful Standards:**
- Resources represented by nouns in URLs
- HTTP methods for actions (GET, POST, PUT, PATCH, DELETE)
- Stateless requests
- Consistent response formats
- Proper HTTP status codes

**Authentication:**
- JWT token in Authorization header: `Authorization: Bearer <token>`
- Token refresh mechanism
- Logout invalidates refresh token

**Response Format:**
```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Success message",
  "errors": null,
  "metadata": {
    "timestamp": "2026-01-19T10:30:00Z",
    "request_id": "uuid"
  }
}
```

### 8.2 Core API Endpoints

#### 8.2.1 Authentication Endpoints

**POST /api/auth/register/**
- **Description:** Register new user (based on permissions)
- **Permission:** Varies by role being created
- **Request:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "teacher",
  "school_id": 123,
  "password": "temporary_password"
}
```
- **Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "user_id": 456,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "teacher"
  }
}
```

**POST /api/auth/login/**
- **Description:** Authenticate user and receive tokens
- **Permission:** Public
- **Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
- **Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 456,
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "teacher",
      "school_id": 123
    }
  }
}
```

**POST /api/auth/token/refresh/**
- **Description:** Refresh access token
- **Request:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**POST /api/auth/logout/**
- **Description:** Invalidate refresh token
- **Permission:** Authenticated

#### 8.2.2 User Management Endpoints

**GET /api/users/**
- **Description:** List users (filtered by scope)
- **Permission:** IsAdminOrManager
- **Query Parameters:**
  - `role` - Filter by role
  - `school_id` - Filter by school
  - `is_active` - Filter active/inactive
  - `search` - Search by name or email
  - `page` - Pagination page number
  - `page_size` - Results per page
- **Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": 456,
        "email": "teacher@school.com",
        "full_name": "Jane Smith",
        "role": "teacher",
        "school": {
          "id": 123,
          "name": "Hope Academy"
        },
        "is_active": true,
        "date_joined": "2025-09-01T00:00:00Z"
      }
    ],
    "count": 1,
    "next": null,
    "previous": null
  }
}
```

**POST /api/users/create/**
- **Description:** Create new user
- **Permission:** Varies by role

**PATCH /api/users/{user_id}/**
- **Description:** Update user information
- **Permission:** IsAdminOrManager

**POST /api/users/{user_id}/deactivate/**
- **Description:** Deactivate user account
- **Permission:** IsAdminOrManager

**POST /api/users/{user_id}/activate/**
- **Description:** Reactivate user account
- **Permission:** IsAdminOrManager

#### 8.2.3 Academic Management Endpoints

**GET /api/students/{student_id}/grades/**
- **Description:** Get student grades
- **Permission:** IsStudent (own), IsGuardian (linked child), IsTeacher (assigned students), IsManager
- **Query Parameters:**
  - `classroom_id` - Filter by class
  - `academic_year` - Filter by year
  - `assignment_type` - Filter by assignment type
- **Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "student": {
      "id": 789,
      "name": "Student Name",
      "current_gpa": 3.75
    },
    "grades": [
      {
        "id": 1001,
        "assignment": {
          "title": "Math Quiz 1",
          "type": "quiz",
          "due_date": "2025-10-15"
        },
        "classroom": {
          "name": "Mathematics Grade 10",
          "teacher": "Mr. Johnson"
        },
        "score": 85,
        "max_score": 100,
        "percentage": 85.00,
        "letter_grade": "B",
        "graded_at": "2025-10-16T14:30:00Z",
        "teacher_comments": "Good work!"
      }
    ]
  }
}
```

**POST /api/grades/**
- **Description:** Create grade entry
- **Permission:** IsTeacher
- **Request:**
```json
{
  "student_id": 789,
  "assignment_id": 501,
  "score": 85,
  "max_score": 100,
  "teacher_comments": "Good work!"
}
```

**GET /api/attendance/**
- **Description:** Get attendance records
- **Permission:** Varies by role
- **Query Parameters:**
  - `student_id` - Filter by student
  - `classroom_id` - Filter by classroom
  - `date_from` - Start date
  - `date_to` - End date
  - `status` - Filter by status

**POST /api/attendance/**
- **Description:** Record attendance
- **Permission:** IsTeacher
- **Request:**
```json
{
  "classroom_id": 301,
  "date": "2026-01-19",
  "records": [
    {
      "student_id": 789,
      "status": "present",
      "check_in_time": "08:00:00"
    },
    {
      "student_id": 790,
      "status": "absent",
      "notes": "Called in sick"
    }
  ]
}
```

**GET /api/assignments/**
- **Description:** List assignments
- **Permission:** Varies by role
- **Query Parameters:**
  - `classroom_id` - Filter by classroom
  - `student_id` - Get assignments for student
  - `due_date_from` - Filter by due date
  - `is_published` - Only published assignments

**POST /api/assignments/**
- **Description:** Create assignment
- **Permission:** IsTeacher
- **Request:**
```json
{
  "classroom_id": 301,
  "title": "Algebra Homework 5",
  "description": "Complete exercises 1-20 on page 45",
  "assignment_type": "homework",
  "max_score": 100,
  "weight": 10,
  "assigned_date": "2026-01-19",
  "due_date": "2026-01-26",
  "is_published": true
}
```

#### 8.2.4 Communication Endpoints

**GET /api/notifications/**
- **Description:** Get user notifications
- **Permission:** Authenticated
- **Query Parameters:**
  - `is_read` - Filter read/unread
  - `notification_type` - Filter by type
  - `limit` - Number of results

**PATCH /api/notifications/{id}/mark-read/**
- **Description:** Mark notification as read
- **Permission:** Authenticated (own notifications)

**POST /api/messages/**
- **Description:** Send message
- **Permission:** Varies by role
- **Request:**
```json
{
  "recipient_ids": [456, 457],
  "subject": "Meeting Request",
  "body": "Can we schedule a meeting to discuss...",
  "attachments": []
}
```

**GET /api/messages/threads/**
- **Description:** Get message threads
- **Permission:** Authenticated
- **Response:** Message threads with latest message

**GET /api/messages/thread/{thread_id}/**
- **Description:** Get full conversation thread
- **Permission:** Authenticated (participant only)

**POST /api/announcements/**
- **Description:** Broadcast announcement
- **Permission:** IsAdminOrManager
- **Request:**
```json
{
  "target_scope": "school",
  "scope_id": 123,
  "title": "School Closure Notice",
  "message": "Due to weather conditions...",
  "priority": "high"
}
```

#### 8.2.5 Reporting Endpoints

**POST /api/reports/student-performance/**
- **Description:** Generate student performance report
- **Permission:** IsTeacher, IsManager, IsGuardian (own child)
- **Request:**
```json
{
  "student_id": 789,
  "date_from": "2025-09-01",
  "date_to": "2026-01-19",
  "include_charts": true,
  "format": "pdf"
}
```
- **Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "report_url": "https://storage.example.com/reports/student_789_report.pdf",
    "expires_at": "2026-01-20T10:30:00Z"
  }
}
```

**GET /api/reports/school-analytics/**
- **Description:** Get school-level analytics
- **Permission:** IsSchoolManager
- **Query Parameters:**
  - `school_id` - School ID
  - `academic_year` - Filter by year
  - `metric_type` - attendance, performance, enrollment

**GET /api/reports/workstream-analytics/**
- **Description:** Get workstream-level analytics
- **Permission:** IsWorkstreamManager
- **Query Parameters:**
  - `workstream_id` - Workstream ID
  - `comparison_type` - school_comparison, trends

### 8.3 API Versioning

**Version Strategy:** URL path versioning
- Current version: `/api/v1/`
- Future versions: `/api/v2/`, etc.

**Backward Compatibility:**
- Maintain previous version for 6 months after new version release
- Deprecation warnings in API responses
- Clear migration documentation

### 8.4 Rate Limiting

**Rate Limits:**
- Authenticated users: 1000 requests/hour
- Unauthenticated: 100 requests/hour
- Report generation: 50 requests/hour
- File uploads: 100 requests/hour

**Implementation:** Redis-based token bucket algorithm

**Rate Limit Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1642593600
```

### 8.5 Error Handling

**Standard Error Response:**
```json
{
  "success": false,
  "data": null,
  "message": "Validation error",
  "errors": [
    {
      "field": "email",
      "code": "unique",
      "message": "This email address is already registered"
    }
  ],
  "metadata": {
    "timestamp": "2026-01-19T10:30:00Z",
    "request_id": "uuid"
  }
}
```

**HTTP Status Codes:**
- `200 OK` - Successful GET/PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing/invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

## 9. User Stories and Scenarios

### 9.1 Admin User Stories

**US-ADMIN-001: Create Workstream Manager**
- **As an** Admin
- **I want to** create Workstream Manager accounts
- **So that** I can delegate management of school groups

**Acceptance Criteria:**
- Admin can navigate to User Management
- Can select "Workstream Manager" role
- Can assign to specific workstream
- New manager receives credentials
- Manager appears in user list

**Test Scenario:**
1. Admin logs into system
2. Navigates to User Management → Add User
3. Enters manager details (name, email)
4. Selects "Workstream Manager" role
5. Assigns to "Northern Region" workstream
6. Clicks "Save"
7. System creates account and sends welcome email
8. Manager can log in with credentials

---

**US-ADMIN-002: View System Analytics**
- **As an** Admin
- **I want to** view system-wide analytics
- **So that** I can monitor platform health and usage

**Acceptance Criteria:**
- Dashboard shows active users by role
- System performance metrics visible
- Usage trends displayed with charts
- Can drill down into specific metrics
- Data export capability

---

### 9.2 Workstream Manager User Stories

**US-WSMGR-001: Create School**
- **As a** Workstream Manager
- **I want to** create new school entities
- **So that** I can expand the workstream's reach

**Acceptance Criteria:**
- Can access School Management section
- Form captures: name, location, capacity, contact info
- School is linked to manager's workstream automatically
- School appears in workstream's school list
- Can assign School Manager immediately or later

**Test Scenario:**
1. Workstream Manager logs in
2. Navigates to School Management
3. Clicks "Add New School"
4. Enters school details:
   - Name: "Hope Academy"
   - Location: "Damascus, Syria"
   - Capacity: 500 students
   - Contact: admin@hopeacademy.edu
5. Clicks "Save"
6. School created successfully
7. Manager prompted to assign School Manager

---

**US-WSMGR-002: View Cross-School Reports**
- **As a** Workstream Manager
- **I want to** compare performance across schools
- **So that** I can identify best practices and struggling schools

**Acceptance Criteria:**
- Can access Workstream Analytics dashboard
- See comparative metrics for all schools
- Metrics include: enrollment, attendance %, avg GPA
- Can filter by time period
- Can identify top and bottom performing schools
- Can drill down into individual school details

---

### 9.3 School Manager User Stories

**US-SCHMGR-001: Create Teacher Account**
- **As a** School Manager
- **I want to** create teacher accounts
- **So that** I can staff my school

**Acceptance Criteria:**
- Can access User Management
- Can create user with "Teacher" role
- Teacher automatically linked to manager's school
- Can assign subjects/courses during creation
- Teacher receives credentials

**Test Scenario:**
1. School Manager logs in
2. Navigates to User Management → Add Teacher
3. Enters teacher details
4. Assigns to Mathematics department
5. Clicks "Save"
6. Teacher account created
7. Welcome email sent to teacher

---

**US-SCHMGR-002: View School Performance Dashboard**
- **As a** School Manager
- **I want to** monitor overall school performance
- **So that** I can make informed decisions

**Acceptance Criteria:**
- Dashboard shows: enrollment, attendance %, avg GPA
- Department comparisons visible
- Trending data (improving/declining)
- Teacher performance summary
- Can access detailed reports

---

### 9.4 Teacher User Stories

**US-TEACH-001: Record Daily Attendance**
- **As a** Teacher
- **I want to** quickly mark student attendance
- **So that** I can track student presence

**Acceptance Criteria:**
- Can access Attendance module
- Can select class and date
- Student list displayed
- Can mark: Present, Absent, Late, Excused
- Can add notes for absences
- Saves successfully
- Parents/guardians notified of absences

**Test Scenario:**
1. Teacher logs in at start of class
2. Navigates to Attendance
3. Selects "Grade 10 Mathematics" and today's date
4. Class roster loads (30 students)
5. Marks attendance for each student
6. Adds note: "Ali - called in sick"
7. Clicks "Save Attendance"
8. Success message displayed
9. Parents of absent students receive notification

---

**US-TEACH-002: Enter Grades**
- **As a** Teacher
- **I want to** enter assignment grades
- **So that** students and parents can track progress

**Acceptance Criteria:**
- Can select class and assignment
- Student list with grade entry fields
- Can enter numeric scores
- System calculates percentage automatically
- Can add feedback comments
- Students/guardians see grades immediately

---

**US-TEACH-003: Upload Learning Materials**
- **As a** Teacher
- **I want to** upload course materials
- **So that** students can access resources

**Acceptance Criteria:**
- Can access Content Management
- Can upload files (PDF, DOC, PPT, images)
- File size limit: 50MB
- Can organize by topic/unit
- Students see materials in their portal
- Can track who accessed materials

---

### 9.5 Secretary User Stories

**US-SEC-001: Register New Student**
- **As a** Secretary
- **I want to** register new students
- **So that** they can enroll in the school

**Acceptance Criteria:**
- Can access Student Registration
- Form captures all required information
- Can assign to grade level
- Can link to guardian (existing or create new)
- Can enroll in classes
- Student account created successfully

**Test Scenario:**
1. Secretary logs in
2. Navigates to Student Registration
3. Enters student information:
   - Full Name: "Fatima Al-Hassan"
   - DOB: 2010-03-15
   - Grade: 9
   - National ID: 12345678
4. Creates guardian account:
   - Name: "Mohammed Al-Hassan"
   - Relationship: Father
   - Email: mohammed@example.com
5. Links student to guardian
6. Enrolls in Grade 9 classes
7. Clicks "Complete Registration"
8. Student and guardian accounts created
9. Welcome emails sent

---

**US-SEC-002: Generate Student List**
- **As a** Secretary
- **I want to** generate student enrollment lists
- **So that** I can provide administrative reports

**Acceptance Criteria:**
- Can filter by grade, status, enrollment date
- Can export as PDF, Excel, CSV
- List includes: name, ID, grade, contact info
- Can print directly

---

### 9.6 Student User Stories

**US-STU-001: View My Grades**
- **As a** Student
- **I want to** see all my grades
- **So that** I can track my academic performance

**Acceptance Criteria:**
- Dashboard shows grade summary
- Can filter by subject
- See individual assignment grades
- View teacher comments
- See current GPA
- View grade trends (charts)

**Test Scenario:**
1. Student logs in
2. Navigates to Grades section
3. Sees all subjects with current grades
4. Clicks on "Mathematics"
5. Sees all math assignments and scores
6. Views teacher feedback
7. Sees current math grade: B+ (87%)

---

**US-STU-002: Access Learning Materials**
- **As a** Student
- **I want to** access course materials
- **So that** I can study effectively

**Acceptance Criteria:**
- Can browse materials by subject
- Can search for specific content
- Can download files
- Can view PDFs in browser
- Materials available offline (PWA)

---

**US-STU-003: View Attendance Record**
- **As a** Student
- **I want to** see my attendance history
- **So that** I know if I have excessive absences

**Acceptance Criteria:**
- Can view attendance by subject
- See attendance percentage
- View calendar with attendance marked
- See total absences, lates

---

### 9.7 Guardian User Stories

**US-GUARD-001: Monitor Child's Progress**
- **As a** Guardian
- **I want to** view my child's grades and attendance
- **So that** I can support their education

**Acceptance Criteria:**
- Dashboard shows child's summary
- Can view all grades
- Can view attendance records
- Can see upcoming assignments
- Can read teacher comments
- If multiple children, can switch between them

**Test Scenario:**
1. Guardian logs in
2. Sees dashboard for child "Fatima"
3. Views current GPA: 3.5
4. Checks attendance: 95% (2 absences)
5. Reviews recent grades
6. Sees upcoming assignment due Friday
7. Switches to second child "Ahmed"
8. Reviews Ahmed's progress

---

**US-GUARD-002: Communicate with Teachers**
- **As a** Guardian
- **I want to** message my child's teachers
- **So that** I can discuss their progress

**Acceptance Criteria:**
- Can view list of child's teachers
- Can send direct messages
- Can view conversation history
- Teachers can respond
- Receive notifications of replies

---

## 10. Testing Requirements

### 10.1 Testing Strategy

**Testing Pyramid:**
```
        /\
       /  \  E2E Tests (10%)
      /____\
     /      \  Integration Tests (30%)
    /________\
   /          \  Unit Tests (60%)
  /____________\
```

### 10.2 Unit Testing

**Scope:** Individual functions, methods, and components

**Framework:** 
- Backend: pytest, pytest-django
- Frontend: Jest, React Testing Library

**Coverage Requirements:**
- Minimum: 80% code coverage
- Critical modules: 90% coverage
- Models, serializers, permissions: 100% coverage

**Example Unit Tests:**

```python
# Test: User creation validation
def test_create_user_without_email_raises_error():
    with pytest.raises(ValueError):
        CustomUser.objects.create_user(email=None, password='test123')

# Test: Permission checking
def test_teacher_cannot_access_admin_endpoint(api_client, teacher_user):
    api_client.force_authenticate(user=teacher_user)
    response = api_client.get('/api/users/')
    assert response.status_code == 403

# Test: Grade calculation
def test_grade_percentage_calculated_correctly():
    grade = Grade(score=85, max_score=100)
    grade.calculate_percentage()
    assert grade.percentage == 85.0
```

**Test Cases to Cover:**
- Model validation and constraints
- Serializer validation
- Permission classes for all roles
- Business logic calculations
- Utility functions
- API endpoint responses

### 10.3 Integration Testing

**Scope:** Multiple components working together

**Test Scenarios:**
1. **User Registration Flow:**
   - Secretary creates student account
   - Student profile created
   - Guardian linked
   - Welcome emails sent
   - Student can log in

2. **Grade Entry Flow:**
   - Teacher creates assignment
   - Teacher enters grades
   - Grades visible to students
   - Notifications sent to guardians
   - GPA updated

3. **Attendance Recording Flow:**
   - Teacher marks attendance
   - Attendance saved to database
   - Statistics updated
   - Absent notifications sent

4. **Report Generation Flow:**
   - Manager requests report
   - Data aggregated from database
   - Report generated (PDF)
   - Report stored in cloud
   - Download URL returned

**Example Integration Test:**

```python
def test_complete_student_registration_flow(api_client, secretary_user, school):
    # Authenticate as secretary
    api_client.force_authenticate(user=secretary_user)
    
    # Create student
    student_data = {
        'email': 'newstudent@school.com',
        'full_name': 'Test Student',
        'role': 'student',
        'date_of_birth': '2010-01-01',
        'grade_level': 9
    }
    response = api_client.post('/api/users/create/', student_data)
    assert response.status_code == 201
    student_id = response.data['data']['user_id']
    
    # Create guardian
    guardian_data = {
        'email': 'parent@example.com',
        'full_name': 'Test Parent',
        'role': 'guardian'
    }
    response = api_client.post('/api/users/create/', guardian_data)
    assert response.status_code == 201
    guardian_id = response.data['data']['user_id']
    
    # Link student and guardian
    link_data = {
        'student_id': student_id,
        'guardian_id': guardian_id,
        'relationship_type': 'parent'
    }
    response = api_client.post('/api/students/link-guardian/', link_data)
    assert response.status_code == 201
    
    # Verify linkage
    response = api_client.get(f'/api/students/{student_id}/guardians/')
    assert len(response.data['data']) == 1
    assert response.data['data'][0]['guardian_id'] == guardian_id
```

### 10.4 System Testing

**Scope:** End-to-end testing of complete system

**Test Scenarios:**

**TC-SYS-001: Complete Academic Cycle**
1. Admin creates workstream and manager
2. Workstream manager creates school and assigns school manager
3. School manager creates teacher and secretary accounts
4. Secretary registers students and guardians
5. Teacher creates lesson plans and assignments
6. Teacher records attendance
7. Teacher enters grades
8. Students view grades and materials
9. Guardians receive notifications and view child's progress
10. Manager generates performance reports

**TC-SYS-002: Multi-Role Communication**
1. Teacher sends announcement to class
2. All students receive notification
3. Guardians receive notification about their children
4. Guardian replies to teacher
5. Teacher receives and responds to message
6. Conversation thread maintained

**TC-SYS-003: Offline Functionality**
1. User loads application while online
2. User goes offline (network disconnected)
3. User can still view cached dashboards
4. User can still access downloaded materials
5. User attempts to enter grades (queued)
6. User reconnects to network
7. Queued actions synchronized
8. All data updated successfully

### 10.5 User Acceptance Testing (UAT)

**Participants:**
- Actual teachers from pilot schools
- School administrators
- Students (age-appropriate)
- Parents/guardians

**UAT Process:**
1. **Preparation:**
   - Create test accounts for all roles
   - Populate with realistic test data
   - Prepare UAT scripts and checklists

2. **Execution:**
   - Users perform real-world tasks
   - Observers document issues and feedback
   - Users complete satisfaction surveys

3. **Evaluation:**
   - Review feedback and issues
   - Prioritize bugs and improvements
   - Make necessary adjustments

**UAT Test Cases:**

**UAT-TEACHER-001: Daily Attendance Entry**
- **Task:** Mark attendance for morning class
- **Steps:** Log in → Select class → Mark attendance → Save
- **Success Criteria:** Completed in under 2 minutes, all students marked
- **User Feedback:** Ease of use rating 1-5

**UAT-STUDENT-001: View Recent Grades**
- **Task:** Check grades from last week
- **Steps:** Log in → Navigate to grades → Filter by date
- **Success Criteria:** Grades found and displayed clearly
- **User Feedback:** Information clarity rating 1-5

**UAT-GUARDIAN-001: Check Child's Progress**
- **Task:** Review child's academic status
- **Steps:** Log in → View dashboard → Check grades and attendance
- **Success Criteria:** All information accessible, understandable
- **User Feedback:** Usefulness rating 1-5

### 10.6 Performance Testing

**Tools:** 
- Apache JMeter or Locust for load testing
- Django Debug Toolbar for query optimization
- New Relic or DataDog for monitoring

**Test Scenarios:**

**PERF-001: Concurrent User Load**
- **Objective:** Verify system handles 10,000 concurrent users
- **Metrics:** Response time, error rate, throughput
- **Success Criteria:** 
  - 95% of requests < 2s response time
  - Error rate < 1%
  - No system crashes

**PERF-002: Database Query Performance**
- **Objective:** Ensure efficient database queries
- **Metrics:** Query execution time, number of queries per request
- **Success Criteria:**
  - No N+1 query problems
  - Dashboard loads with < 10 queries
  - Individual queries < 100ms

**PERF-003: Report Generation Performance**
- **Objective:** Test report generation under load
- **Metrics:** Generation time, memory usage
- **Success Criteria:**
  - Standard report < 30s
  - Large report (500+ students) < 2 minutes
  - Memory usage stable

**Load Testing Profile:**
```
Ramp-up Period: 5 minutes
Peak Load: 10,000 concurrent users
Sustained Load Duration: 30 minutes
User Mix:
  - 40% Students (viewing grades, content)
  - 30% Teachers (entering data)
  - 20% Guardians (viewing child data)
  - 10% Managers (generating reports)
```

### 10.7 Security Testing

**Test Areas:**

**SEC-001: Authentication & Authorization**
- Test login with invalid credentials
- Test SQL injection in login form
- Test password strength requirements
- Test session timeout
- Test token expiration and refresh
- Test role-based access control for all endpoints
- Test privilege escalation attempts

**SEC-002: Data Validation**
- Test XSS prevention in all input fields
- Test CSRF protection on state-changing operations
- Test file upload validation (type, size, content)
- Test SQL injection in all forms
- Test command injection prevention

**SEC-003: Data Privacy**
- Verify users can only access authorized data
- Test data isolation between schools
- Verify guardians can only see linked children
- Test audit log completeness

**Security Test Cases:**

```python
def test_user_cannot_access_other_school_data(api_client, teacher_user, other_school):
    api_client.force_authenticate(user=teacher_user)
    # Attempt to access student from different school
    response = api_client.get(f'/api/students/{other_school_student_id}/')
    assert response.status_code == 403

def test_xss_prevention_in_message_body(api_client, teacher_user):
    api_client.force_authenticate(user=teacher_user)
    malicious_content = '<script>alert("XSS")</script>'
    response = api_client.post('/api/messages/', {
        'recipient_ids': [123],
        'subject': 'Test',
        'body': malicious_content
    })
    # Verify script tags are escaped/sanitized
    message = Message.objects.latest('id')
    assert '<script>' not in message.body
```

### 10.8 Usability Testing

**Methods:**
- Think-aloud protocols
- Task completion analysis
- Heuristic evaluation
- Accessibility testing

**Usability Metrics:**
- Task completion rate
- Time to complete tasks
- Error rate
- User satisfaction (SUS - System Usability Scale)

**Test Scenarios:**

**USAB-001: First-Time User Onboarding**
- **Task:** New teacher completes first login and explores dashboard
- **Metrics:** Time to understand interface, number of help requests
- **Success:** 80% of users can navigate without assistance

**USAB-002: Mobile Usability**
- **Task:** Guardian checks child's grades on mobile device
- **Metrics:** Touch target size, readability, navigation ease
- **Success:** All critical functions accessible and usable on mobile

### 10.9 Compatibility Testing

**Browser Testing Matrix:**

| Browser | Versions | Priority |
|---------|----------|----------|
| Chrome | Latest 2 | High |
| Firefox | Latest 2 | High |
| Safari | Latest 2 | High |
| Edge | Latest 2 | Medium |
| Mobile Safari (iOS) | iOS 13+ | High |
| Chrome Mobile (Android) | Android 8+ | High |

**Device Testing:**
- Desktop (Windows, macOS, Linux)
- Tablets (iPad, Android tablets)
- Smartphones (iOS, Android)
- Various screen sizes (320px to 2560px width)

### 10.10 Accessibility Testing

**WCAG 2.1 Level AA Compliance Testing:**

**ACCESS-001: Keyboard Navigation**
- Test all functionality accessible via keyboard
- Test tab order is logical
- Test focus indicators visible

**ACCESS-002: Screen Reader Compatibility**
- Test with NVDA (Windows)
- Test with JAWS (Windows)
- Test with VoiceOver (macOS, iOS)
- Verify ARIA labels are appropriate

**ACCESS-003: Visual Accessibility**
- Test color contrast ratios (4.5:1 minimum)
- Test text resizing up to 200%
- Test with different color blindness simulations

**Tools:**
- WAVE (Web Accessibility Evaluation Tool)
- aXe DevTools
- Lighthouse Accessibility Audit

### 10.11 Test Data Management

**Test Data Requirements:**
- Realistic student names, ages, grades
- Various grade distributions
- Diverse attendance patterns
- Multiple schools and workstreams
- Different user roles and permissions

**Test Data Generation:**
```python
# Example test data factory
class StudentFactory:
    @staticmethod
    def create_batch(count=100, school=None):
        students = []
        for i in range(count):
            student = CustomUser.objects.create_user(
                email=f'student{i}@testschool.com',
                full_name=fake.name(),
                role='student',
                school=school
            )
            StudentProfile.objects.create(
                user=student,
                date_of_birth=fake.date_of_birth(minimum_age=10, maximum_age=18),
                grade_level=random.randint(6, 12)
            )
            students.append(student)
        return students
```

### 10.12 Test Automation

**CI/CD Integration:**
- Automated unit tests run on every commit
- Integration tests run on pull requests
- Full test suite runs nightly
- Performance tests run weekly

**Test Automation Tools:**
- **Backend:** pytest, pytest-django, factory_boy
- **Frontend:** Jest, React Testing Library, Cypress
- **E2E:** Selenium, Playwright
- **API:** Postman/Newman, REST Assured

**Continuous Integration Pipeline:**
```yaml
# Example GitHub Actions workflow
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest --cov=. --cov-report=xml
      - name: Run integration tests
        run: pytest tests/integration/
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## 11. Security Requirements

### 11.1 Authentication Security

**Password Policy:**
- Minimum length: 8 characters
- Complexity: uppercase, lowercase, number, special character
- Password history: Cannot reuse last 5 passwords
- Expiration: 90 days (configurable per school)
- Temporary passwords: Expire after first use or 24 hours

**Account Lockout:**
- Failed attempts threshold: 5 consecutive failures
- Lockout duration: 30 minutes
- Progressive delay: Increasing wait time after each failure
- Admin notification: Alert on multiple lockout attempts

**Session Management:**
- JWT access token lifetime: 1 hour
- JWT refresh token lifetime: 7 days
- Automatic logout after 30 minutes inactivity
- Concurrent session limit: 3 devices per user
- Secure token storage: httpOnly cookies (web), secure storage (mobile)

### 11.2 Authorization Security

**Role-Based Access Control (RBAC):**
- Principle of least privilege
- Permission checks at multiple layers (API, service, database)
- No permission inheritance (explicit grants only)
- Regular permission audits

**Data Isolation:**
- Multi-tenancy enforced at database level
- Users can only access data within their scope (workstream/school)
- Query filters automatically applied based on user context
- Cross-tenant access attempts logged and blocked

### 11.3 Data Security

**Encryption:**
- **In Transit:** TLS 1.2+ for all communications
- **At Rest:** AES-256 encryption for sensitive data
- **Database:** Encrypted columns for PII (passwords, national IDs, addresses)
- **Backups:** Encrypted backup storage

**Data Classification:**
- **Public:** School contact information, course catalog
- **Internal:** User roles, school structure
- **Confidential:** Student grades, attendance, personal information
- **Restricted:** Passwords, national IDs, health information

**Data Retention:**
- Active data: Retained indefinitely
- Graduated students: 7 years
- Deleted accounts: Soft delete with 30-day recovery period
- Logs: 90 days (application), 7 years (audit)

### 11.4 Application Security

**Input Validation:**
```python
# Example: Sanitize and validate user input
from django.core.validators import validate_email
from bleach import clean

def sanitize_user_input(data):
    # Remove potentially harmful HTML/JavaScript
    cleaned_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Allow only safe HTML tags if any
            cleaned_data[key] = clean(value, tags=[], strip=True)
        else:
            cleaned_data[key] = value
    return cleaned_data
```

**SQL Injection Prevention:**
- Always use parameterized queries (Django ORM)
- No raw SQL without parameterization
- Input validation on all database queries

**XSS Prevention:**
- Output encoding for all user-generated content
- Content Security Policy (CSP) headers
- Sanitize HTML input
- React's built-in XSS protection

**CSRF Protection:**
- CSRF tokens for all state-changing requests
- SameSite cookie attribute
- Origin validation

### 11.5 API Security

**Rate Limiting:**
```python
# Example rate limiting configuration
RATE_LIMITS = {
    'authentication': '5/minute',  # Login attempts
    'api_default': '1000/hour',    # General API calls
    'reports': '50/hour',          # Report generation
    'uploads': '100/hour',         # File uploads
}
```

**API Key Management:**
- No API keys in source code
- Environment variables for secrets
- Regular key rotation
- Separate keys for development/staging/production

**Request Validation:**
- Schema validation for all API requests
- Size limits on request payloads
- File type and size validation for uploads
- URL validation for external links

### 11.6 Infrastructure Security

**Server Hardening:**
- Minimal OS installation
- Regular security updates
- Firewall configuration (only necessary ports open)
- Intrusion detection system (IDS)
- DDoS protection

**Network Security:**
- VPC (Virtual Private Cloud) isolation
- Private subnets for databases
- Bastion hosts for administrative access
- Network segmentation

**Access Control:**
- SSH key-based authentication only
- Multi-factor authentication (MFA) for admin access
- Principle of least privilege for service accounts
- Regular access reviews

### 11.7 Monitoring and Incident Response

**Security Monitoring:**
- Real-time intrusion detection
- Failed login attempt monitoring
- Unusual access pattern detection
- File integrity monitoring
- Log aggregation and analysis

**Audit Logging:**
```python
# Example audit log entry
{
    "timestamp": "2026-01-19T10:30:00Z",
    "user_id": 456,
    "action": "grade_modified",
    "resource_type": "grade",
    "resource_id": 789,
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "old_value": {"score": 80},
    "new_value": {"score": 85},
    "status": "success"
}
```

**Logged Events:**
- Authentication (success and failure)
- Authorization failures
- Data modifications (grades, attendance, user accounts)
- Configuration changes
- File uploads/downloads
- Report generation
- Admin actions

**Incident Response Plan:**
1. **Detection:** Automated alerts for security events
2. **Assessment:** Determine severity and impact
3. **Containment:** Isolate affected systems
4. **Eradication:** Remove threat/vulnerability
5. **Recovery:** Restore normal operations
6. **Lessons Learned:** Post-incident analysis

### 11.8 Compliance and Privacy

**Data Protection Compliance:**
- GDPR compliance for EU users
- Data processing agreements
- Privacy policy clearly stated
- User consent management
- Right to access, rectify, delete personal data
- Data portability

**Data Subject Rights:**
- **Right to Access:** Users can request all their data
- **Right to Rectification:** Users can correct inaccurate data
- **Right to Erasure:** Users can request account deletion
- **Right to Portability:** Data export in standard formats

**Privacy by Design:**
- Data minimization (collect only necessary data)
- Purpose limitation (use data only for stated purposes)
- Storage limitation (delete data when no longer needed)
- Pseudonymization where possible

### 11.9 Secure Development Practices

**Code Security:**
- Mandatory code reviews
- Static code analysis (Bandit for Python, ESLint for JavaScript)
- Dependency vulnerability scanning
- Regular security training for developers

**Secure CI/CD:**
- Automated security scanning in pipeline
- Secret detection in commits
- Container image scanning
- No credentials in code repositories

**Third-Party Dependencies:**
- Regular dependency updates
- Vulnerability monitoring (Dependabot, Snyk)
- License compliance checking
- Minimal dependency footprint

---

## 12. Deployment and Infrastructure

### 12.1 Deployment Architecture

**Cloud Provider:** AWS, Azure, or Google Cloud Platform

**Architecture Diagram:**
```
┌─────────────────────────────────────────────────────┐
│                  CloudFront CDN                      │
│              (Static Assets, Caching)                │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│            Application Load Balancer                 │
│          (SSL Termination, Routing)                  │
└─────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│               Auto Scaling Group                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  App     │  │  App     │  │  App     │          │
│  │ Server 1 │  │ Server 2 │  │ Server N │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└──────────────────────────────────────────────────────┘
                        ↓
┌───────────────────────┬──────────────────────────────┐
│    MySQL RDS          │      Redis ElastiCache       │
│  (Primary + Replica)  │   (Session & Cache Store)    │
└───────────────────────┴──────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              S3 Bucket (File Storage)                │
└─────────────────────────────────────────────────────┘
```

### 12.2 Environment Configuration

**Environments:**
1. **Development:** Local developer machines
2. **Staging:** Pre-production testing environment
3. **Production:** Live user-facing environment

**Environment-Specific Settings:**
```python
# settings/production.py
DEBUG = False
ALLOWED_HOSTS = ['edutraker.com', 'www.edutraker.com']
DATABASE_URL = os.environ.get('DATABASE_URL')
REDIS_URL = os.environ.get('REDIS_URL')
AWS_S3_BUCKET = os.environ.get('S3_BUCKET')
SECRET_KEY = os.environ.get('SECRET_KEY')
```

### 12.3 Database Configuration

**MySQL Setup:**
- **Instance Type:** db.r5.large (production)
- **Storage:** 500GB SSD, auto-scaling enabled
- **Backups:** Automated daily backups, 30-day retention
- **Read Replicas:** 2 replicas for read scaling
- **Multi-AZ:** Enabled for high availability

**Redis Configuration:**
- **Instance Type:** cache.r5.large
- **Cluster Mode:** Enabled for scalability
- **Backup:** Daily snapshots
- **Eviction Policy:** allkeys-lru

### 12.4 Application Server Configuration

**Docker Configuration:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "eduTrack.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

**Gunicorn Configuration:**
- Workers: 4 per instance (2 × CPU cores)
- Timeout: 30 seconds
- Max requests: 1000 (restart workers periodically)
- Keep-alive: 5 seconds

### 12.5 Scaling Strategy

**Horizontal Scaling:**
- Auto-scaling based on CPU utilization (> 70%)
- Minimum instances: 2 (high availability)
- Maximum instances: 20
- Scale-up cooldown: 3 minutes
- Scale-down cooldown: 10 minutes

**Database Scaling:**
- Read replicas for read-heavy operations
- Connection pooling (pgBouncer/ProxySQL)
- Query optimization and indexing
- Vertical scaling for write-heavy workloads

### 12.6 Deployment Process

**CI/CD Pipeline:**
```yaml
# Deployment workflow
1. Developer commits to feature branch
2. Automated tests run (unit, integration)
3. Code review and approval
4. Merge to develop branch
5. Deploy to staging environment
6. Run automated E2E tests on staging
7. Manual QA testing
8. Merge to main branch
9. Deploy to production (blue-green deployment)
10. Health checks and smoke tests
11. Switch traffic to new version
12. Monitor for issues
```

**Blue-Green Deployment:**
- Maintain two identical production environments
- Deploy to inactive environment (green)
- Run health checks and smoke tests
- Switch load balancer to green environment
- Keep blue environment for quick rollback

**Database Migrations:**
```bash
# Safe migration process
1. Backup database
2. Run migration in staging
3. Test application thoroughly
4. Schedule maintenance window (if needed)
5. Run migration in production
6. Verify data integrity
7. Monitor application health
```

### 12.7 Monitoring and Observability

**Application Monitoring:**
- **Tool:** New Relic, DataDog, or Prometheus + Grafana
- **Metrics:**
  - Request rate, response time, error rate
  - Database query performance
  - Cache hit/miss ratio
  - API endpoint performance

**Infrastructure Monitoring:**
- CPU, memory, disk, network utilization
- Auto-scaling events
- Load balancer health
- Database performance metrics

**Log Management:**
- **Tool:** ELK Stack (Elasticsearch, Logstash, Kibana) or Splunk
- **Log Types:** Application, access, error, audit
- **Retention:** 90 days for application logs, 7 years for audit logs
- **Alerts:** Configured for error spikes, security events

**Alerting:**
```yaml
# Example alert rules
- name: High Error Rate
  condition: error_rate > 5%
  duration: 5 minutes
  severity: critical
  notify: [email, slack, pagerduty]

- name: Slow Response Time
  condition: p95_response_time > 2000ms
  duration: 10 minutes
  severity: warning
  notify: [email, slack]

- name: Database Connection Pool Exhausted
  condition: available_connections < 10%
  duration: 1 minute
  severity: critical
  notify: [pagerduty]
```

### 12.8 Backup and Disaster Recovery

**Backup Strategy:**
- **Database:**
  - Automated daily snapshots
  - Point-in-time recovery enabled
  - 30-day retention
  - Cross-region replication
  
- **File Storage:**
  - Versioning enabled on S3
  - Lifecycle policy for old versions
  - Cross-region replication for critical data

- **Application Configuration:**
  - Infrastructure as Code (Terraform/CloudFormation)
  - Version controlled configuration files
  - Automated environment provisioning

**Disaster Recovery Plan:**
- **RTO (Recovery Time Objective):** 4 hours
- **RPO (Recovery Point Objective):** 6 hours
- **DR Testing:** Quarterly disaster recovery drills
- **Runbooks:** Documented procedures for common incidents

**Recovery Procedures:**
1. Assess the situation and impact
2. Activate disaster recovery team
3. Restore from most recent backup
4. Verify data integrity
5. Update DNS if needed (failover)
6. Communicate with stakeholders
7. Resume normal operations
8. Conduct post-mortem analysis

### 12.9 Security in Production

**Production Security Measures:**
- WAF (Web Application Firewall) enabled
- DDoS protection activated
- Security groups configured (least privilege)
- Secrets management (AWS Secrets Manager / HashiCorp Vault)
- Regular security scans and penetration testing
- SSL/TLS certificates with auto-renewal

**Access Control:**
- MFA required for production access
- VPN required for administrative access
- Audit logging for all production access
- Separate credentials for each environment
- Regular access audits and reviews

### 12.10 Performance Optimization

**Caching Strategy:**
```python
# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'edutraker',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Cache key examples
USER_PROFILE_CACHE_KEY = 'user:profile:{user_id}'
STUDENT_GRADES_CACHE_KEY = 'student:{student_id}:grades'
SCHOOL_STATS_CACHE_KEY = 'school:{school_id}:stats'
```

**Database Optimization:**
- Connection pooling (max 100 connections)
- Query optimization (use select_related, prefetch_related)
- Database indexes on frequently queried fields
- Read replicas for read-heavy queries
- Periodic ANALYZE and VACUUM operations

**Frontend Optimization:**
- Code splitting and lazy loading
- Image optimization and lazy loading
- Service worker for offline caching
- CDN for static assets
- Gzip/Brotli compression

### 12.11 Cost Optimization

**Resource Right-Sizing:**
- Regular review of instance utilization
- Downsize underutilized resources
- Use spot instances for non-critical workloads
- Reserved instances for predictable workloads

**Storage Optimization:**
- Lifecycle policies for old data
- Compression for archived data
- Cleanup of unused resources
- S3 intelligent tiering

**Monitoring Costs:**
- Set up billing alerts
- Tag resources for cost allocation
- Regular cost analysis and optimization
- Budget tracking per environment

---

## 13. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| Academic Year | The annual period during which school is in session, typically 9-10 months |
| Artifact | A piece of work product or deliverable |
| Assignment | Coursework given to students by teachers |
| Attendance | Record of student presence/absence in class |
| Cascading Configuration | Settings that flow from global to specific levels with ability to override |
| Classroom | A specific section/instance of a course taught by a teacher |
| Course | An academic subject or class |
| GPA | Grade Point Average - cumulative average of student grades |
| Guardian | Parent or legal guardian responsible for a student |
| Knowledge Gap | Areas where a student's understanding or skills are below expected level |
| Multi-Tenant | Architecture where single instance serves multiple organizations (schools) |
| Notification | System-generated message to inform users of events |
| PWA | Progressive Web App - web application that works offline like a native app |
| RBAC | Role-Based Access Control - permissions based on user roles |
| School Manager | Administrator responsible for a single school |
| Secretary | Administrative staff who register students and support operations |
| Workstream | Collection of schools under common management/organization |
| Workstream Manager | Administrator responsible for multiple schools in a workstream |

### Appendix B: Acronyms and Abbreviations

| Acronym | Full Form |
|---------|-----------|
| API | Application Programming Interface |
| AWS | Amazon Web Services |
| CDN | Content Delivery Network |
| CI/CD | Continuous Integration/Continuous Deployment |
| CRUD | Create, Read, Update, Delete |
| CSRF | Cross-Site Request Forgery |
| CSS | Cascading Style Sheets |
| CSV | Comma-Separated Values |
| DB | Database |
| DNS | Domain Name System |
| DR | Disaster Recovery |
| E2E | End-to-End |
| ELK | Elasticsearch, Logstash, Kibana |
| GDPR | General Data Protection Regulation |
| HTML | Hypertext Markup Language |
| HTTP | Hypertext Transfer Protocol |
| HTTPS | Hypertext Transfer Protocol Secure |
| IDS | Intrusion Detection System |
| JWT | JSON Web Token |
| MFA | Multi-Factor Authentication |
| MySQL | My Structured Query Language |
| ORM | Object-Relational Mapping |
| PDF | Portable Document Format |
| PII | Personally Identifiable Information |
| REST | Representational State Transfer |
| RPO | Recovery Point Objective |
| RTO | Recovery Time Objective |
| S3 | Simple Storage Service (AWS) |
| SaaS | Software as a Service |
| SQL | Structured Query Language |
| SRS | Software Requirements Specification |
| SSL | Secure Sockets Layer |
| TLS | Transport Layer Security |
| UAT | User Acceptance Testing |
| UI | User Interface |
| URL | Uniform Resource Locator |
| VPC | Virtual Private Cloud |
| WAF | Web Application Firewall |
| WCAG | Web Content Accessibility Guidelines |
| XSS | Cross-Site Scripting |

### Appendix C: Current System Implementation Status

Based on the provided repository structure, the following modules are currently implemented:

**Implemented Modules:**
- ✅ accounts/ - User authentication and management
- ✅ workstream/ - Workstream management
- ✅ workstream_manager/ - Workstream manager functionality
- ✅ school/ - School entity management
- ✅ student/ - Student-specific features
- ✅ teacher/ - Teacher-specific features
- ✅ guardian/ - Guardian functionality
- ✅ secretary/ - Secretary administrative functions
- ✅ manager/ - Manager dashboards and reports
- ✅ notifications/ - Notification system
- ✅ reports/ - Reporting and analytics
- ✅ user_messages/ - Internal messaging
- ✅ custom_admin/ - Custom admin interface

**Technology Stack (Confirmed):**
- Backend: Django + Django REST Framework
- Database: MySQL (configured in models)
- Authentication: JWT (SimpleJWT)
- Documentation: OpenAPI/Swagger (drf-spectacular)

**Key Models Implemented:**
- CustomUser (with role-based authentication)
- WorkStream
- School
- SystemConfiguration
- Role-based permissions classes

### Appendix D: Future Enhancements (Roadmap)

**Phase 2 (6-12 months):**
- React-based frontend PWA
- Mobile applications (iOS/Android native)
- Advanced analytics and data visualization
- AI-powered knowledge gap identification
- Automated report scheduling
- SMS notifications
- Video content support
- Parent-teacher conference scheduling

**Phase 3 (12-24 months):**
- Learning Management System (LMS) integration
- Virtual classroom capabilities
- Gamification features for student engagement
- Multi-language support (Arabic, French, Spanish)
- Advanced security features (2FA, biometric authentication)
- Integration with external education platforms
- Predictive analytics for student success
- Customizable report templates

**Phase 4 (24+ months):**
- AI teaching assistant
- Personalized learning paths
- Blockchain-based credential verification
- Advanced collaboration tools
- Augmented reality learning experiences
- Parent community features
- Marketplace for educational content
- White-label solutions for different organizations

### Appendix E: Support and Maintenance

**Support Levels:**
- **Level 1:** Basic user support (email, chat)
- **Level 2:** Technical support (bug fixes, configuration)
- **Level 3:** Development team (critical issues, code changes)

**Maintenance Windows:**
- Scheduled: Every Saturday 2:00 AM - 6:00 AM UTC
- Emergency: As needed with 2-hour notice
- Notification: 48 hours advance notice for planned maintenance

**SLA (Service Level Agreement):**
- **Critical Issues:** 2-hour response time, 8-hour resolution
- **High Priority:** 8-hour response time, 24-hour resolution
- **Medium Priority:** 24-hour response time, 72-hour resolution
- **Low Priority:** 48-hour response time, 1-week resolution

**Issue Severity Definitions:**
- **Critical:** System down, data loss, security breach
- **High:** Major functionality broken, many users affected
- **Medium:** Feature not working as expected, workaround available
- **Low:** Minor issue, cosmetic problems, feature requests

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-19 | Development Team | Initial comprehensive SRS based on repository analysis and provided documents |

---

## Approvals

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | | | |
| Technical Lead | | | |
| QA Lead | | | |
| Security Officer | | | |

---

**END OF DOCUMENT**AINT-001: Code Quality
**Priority:** High  
**Description:** The system shall be developed with maintainable, high-quality code.

**Code Standards:**
- PEP 8 compliance for Python code
- ESLint/Prettier for JavaScript/React code
- Comprehensive code comments
- Meaningful variable and function names
- DRY (Don't Repeat Yourself) principle

**Code Review:**
- Peer review required for all changes
- Automated code quality checks (SonarQube or similar)
- Test coverage ≥ 80%
- Documentation updates with code changes

#### NFR-M