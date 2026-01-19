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
        choices=[('parent', AINT-001: Code Quality
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