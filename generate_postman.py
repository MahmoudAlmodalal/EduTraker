
import json

def generate_postman_collection():
    collection = {
        "info": {
            "_postman_id": "edutraker-ultimate-v4",
            "name": "EduTraker - Ultimate API Collection (SRS Aligned)",
            "description": "Fully exhaustive collection covering every endpoint + advanced business flows (Cascading Config, Staff Eval, Student-Guardian Linkage, Report Exports).",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [],
        "variable": [
            {"key": "baseUrl", "value": "http://localhost:8000", "type": "string"},
            {"key": "accessToken", "value": "TOKEN_HERE", "type": "string"},
            {"key": "refreshToken", "value": "TOKEN_HERE", "type": "string"},
            {"key": "workstreamId", "value": "1", "type": "string"},
            {"key": "userId", "value": "2", "type": "string"},
            {"key": "schoolId", "value": "1", "type": "string"},
            {"key": "academicYearId", "value": "1", "type": "string"},
            {"key": "gradeId", "value": "1", "type": "string"},
            {"key": "courseId", "value": "1", "type": "string"},
            {"key": "classroomId", "value": "1", "type": "string"},
            {"key": "teacherId", "value": "1", "type": "string"},
            {"key": "studentId", "value": "1", "type": "string"},
            {"key": "guardianId", "value": "1", "type": "string"},
            {"key": "assignmentId", "value": "1", "type": "string"},
            {"key": "attendanceId", "value": "1", "type": "string"},
            {"key": "markId", "value": "1", "type": "string"},
            {"key": "enrollmentId", "value": "1", "type": "string"},
            {"key": "notificationId", "value": "1", "type": "string"},
            {"key": "messageId", "value": "1", "type": "string"},
            {"key": "threadId", "value": "thread-uuid-1", "type": "string"},
            {"key": "configId", "value": "1", "type": "string"}
        ]
    }

    def create_request(name, method, url, body=None, header=None):
        if header is None:
            header = [{"key": "Authorization", "value": "Bearer {{accessToken}}"}]
        
        # Proper path split for Postman
        path = url.replace("{{baseUrl}}/", "").split("/")
        if path[-1] == "": path.pop()

        req = {
            "name": name,
            "request": {
                "method": method,
                "header": header,
                "url": {
                    "raw": url,
                    "host": ["{{baseUrl}}"],
                    "path": path
                }
            }
        }
        if body:
            req["request"]["body"] = {
                "mode": "raw",
                "raw": json.dumps(body, indent=4),
                "options": {"raw": {"language": "json"}}
            }
        return req

    # --- 01. Authentication ---
    auth_folder = {"name": "01. Authentication", "item": []}
    portal_auth = {"name": "Portal", "item": [
        create_request("Register - Success", "POST", "{{baseUrl}}/api/portal/auth/register/", 
                       {"email": "test@test.com", "full_name": "Test", "password": "Pass123!", "password_confirm": "Pass123!"}, header=[]),
        create_request("Login - Success", "POST", "{{baseUrl}}/api/portal/auth/login/", 
                       {"email": "admin@test.com", "password": "test1234"}, header=[]),
        create_request("Login - 400 Invalid", "POST", "{{baseUrl}}/api/portal/auth/login/", 
                       {"email": "admin@test.com", "password": "wrong"}, header=[]),
    ]}
    auth_folder["item"].append(portal_auth)
    
    ws_auth = {"name": "Workstream", "item": [
        create_request("Login - Success", "POST", "{{baseUrl}}/api/workstream/{{workstreamId}}/auth/login/", 
                       {"email": "ws@test.com", "password": "pass"}, header=[]),
        create_request("Register in WS", "POST", "{{baseUrl}}/api/workstream/{{workstreamId}}/auth/register/", 
                       {"email": "newws@test.com", "full_name": "New", "password": "pass", "password_confirm": "pass"}, header=[]),
    ]}
    auth_folder["item"].append(ws_auth)
    auth_folder["item"].append(create_request("Refresh Token", "POST", "{{baseUrl}}/api/auth/token/refresh/", {"refresh": "{{refreshToken}}"}, header=[]))
    collection["item"].append(auth_folder)

    # --- 02. Accounts & Access ---
    accounts_folder = {"name": "02. Accounts & Access", "item": []}
    accounts_folder["item"].append({"name": "Users", "item": [
        create_request("List All", "GET", "{{baseUrl}}/api/users/"),
        create_request("Create User", "POST", "{{baseUrl}}/api/users/create/", {"email": "u@t.com", "full_name": "U", "password": "P", "role": "admin"}),
        create_request("Update User", "PATCH", "{{baseUrl}}/api/users/{{userId}}/", {"full_name": "Modified"}),
        create_request("403 Forbidden Access", "GET", "{{baseUrl}}/api/users/", header=[{"key": "Authorization", "value": "Bearer INVALID"}]),
    ]})
    collection["item"].append(accounts_folder)

    # --- 03. System Configuration (Cascading) ---
    config_folder = {"name": "03. Configuration (Cascading)", "item": [
        create_request("Get Global Configs", "GET", "{{baseUrl}}/api/system-config/?scope=global"),
        create_request("Get WS Configs", "GET", "{{baseUrl}}/api/system-config/?scope=workstream&work_stream={{workstreamId}}"),
        create_request("Get School Configs", "GET", "{{baseUrl}}/api/system-config/?scope=school&school={{schoolId}}"),
        create_request("Create Global Policy", "POST", "{{baseUrl}}/api/system-config/", {"config_key": "grading_scale", "config_value": "numeric"}),
        create_request("Override for School", "POST", "{{baseUrl}}/api/system-config/", {"config_key": "grading_scale", "config_value": "letter", "school": 1}),
        create_request("Update Config", "PATCH", "{{baseUrl}}/api/system-config/{{configId}}/", {"config_value": "mixed"}),
    ]}
    collection["item"].append(config_folder)

    # --- 04. Workstream & Schools ---
    structure_folder = {"name": "04. Workstream & Schools", "item": []}
    structure_folder["item"].append({"name": "Workstreams", "item": [
        create_request("List Workstreams", "GET", "{{baseUrl}}/api/workstream/"),
        create_request("WS Info", "GET", "{{baseUrl}}/api/workstreams/{{workstreamId}}/info/", header=[]),
        create_request("Update WS", "PUT", "{{baseUrl}}/api/workstreams/{{workstreamId}}/update/", {"workstream_name": "Updated", "capacity": 50}),
    ]})
    structure_folder["item"].append({"name": "Schools", "item": [
        create_request("List Schools", "GET", "{{baseUrl}}/api/school/"),
        create_request("Create School", "POST", "{{baseUrl}}/api/school/create/", {"school_name": "New School", "work_stream": 1, "capacity": 500}),
        create_request("School Detail", "GET", "{{baseUrl}}/api/school/{{schoolId}}/"),
        create_request("Deactivate School", "POST", "{{baseUrl}}/api/school/{{schoolId}}/deactivate/"),
    ]})
    structure_folder["item"].append({"name": "Academic Structure", "item": [
        create_request("List Years", "GET", "{{baseUrl}}/api/academic-years/"),
        create_request("Create Year", "POST", "{{baseUrl}}/api/academic-years/create/", {"academic_year_code": "2025/26", "start_date": "2025-09-01", "end_date": "2026-06-30", "school": 1}),
        create_request("List Grades", "GET", "{{baseUrl}}/api/grades/"),
        create_request("List Courses", "GET", "{{baseUrl}}/api/school/{{schoolId}}/courses/"),
        create_request("Create Classroom", "POST", "{{baseUrl}}/api/school/{{schoolId}}/academic-year/{{academicYearId}}/class-rooms/create/", {"classroom_name": "B-102", "grade": 1, "academic_year": 1}),
    ]})
    collection["item"].append(structure_folder)

    # --- 05. Staff & Teacher Operations ---
    staff_folder = {"name": "05. Staff Operations", "item": []}
    staff_folder["item"].append({"name": "Secretaries", "item": [
        create_request("List Secretaries", "GET", "{{baseUrl}}/api/secretary/secretaries/"),
        create_request("Create Secretary", "POST", "{{baseUrl}}/api/secretary/secretaries/create/", 
                       {"email": "sec@school.com", "full_name": "Sec One", "password": "pass", "school_id": 1, "department": "Admin", "hire_date": "2026-01-01"}),
    ]})
    staff_folder["item"].append({"name": "Teachers", "item": [
        create_request("List Teachers", "GET", "{{baseUrl}}/api/teacher/teachers/"),
        create_request("Create Teacher", "POST", "{{baseUrl}}/api/teacher/teachers/create/", 
                       {"email": "teacher@school.com", "full_name": "Prof Test", "password": "pass", "school_id": 1, "specialization": "Math", "hire_date": "2026-01-01", "employment_status": "full_time"}),
        create_request("Teacher Dashboard Stats", "GET", "{{baseUrl}}/api/statistics/teacher/{{teacherId}}/"),
    ]})
    staff_folder["item"].append({"name": "Staff Evaluation (SRS FR-RA-005)", "item": [
        create_request("List Evaluations", "GET", "{{baseUrl}}/api/manager/staff-evaluations/"),
        create_request("Create Evaluation", "POST", "{{baseUrl}}/api/manager/staff-evaluations/", 
                       {"reviewee": 5, "reviewer": 2, "evaluation_date": "2026-01-20", "rating_score": 5, "comments": "Excellent performance"}),
        create_request("Evaluation Details", "GET", "{{baseUrl}}/api/manager/staff-evaluations/{{configId}}/"),
    ]})
    collection["item"].append(staff_folder)

    # --- 06. Academic Operations (Teachers) ---
    academic_folder = {"name": "06. Academic Ops (Teacher)", "item": []}
    academic_folder["item"].append({"name": "Assignments", "item": [
        create_request("List Assignments", "GET", "{{baseUrl}}/api/teacher/assignments/"),
        create_request("Create Quiz", "POST", "{{baseUrl}}/api/teacher/assignments/", {"title": "Math Quiz 1", "assignment_type": "quiz", "full_mark": 50, "weight": 1.5}),
        create_request("Create Final Exam", "POST", "{{baseUrl}}/api/teacher/assignments/", {"title": "Final Exam", "assignment_type": "final", "full_mark": 100, "weight": 3.0}),
    ]})
    academic_folder["item"].append({"name": "Grading (Marks)", "item": [
        create_request("Record Success Mark", "POST", "{{baseUrl}}/api/teacher/marks/record/", {"student_id": 1, "assignment_id": 1, "score": 45, "feedback": "Great work"}),
        create_request("Fail: Score > Full Mark", "POST", "{{baseUrl}}/api/teacher/marks/record/", {"student_id": 1, "assignment_id": 1, "score": 999}),
        create_request("Update Mark", "PATCH", "{{baseUrl}}/api/teacher/marks/{{markId}}/", {"score": 48}),
    ]})
    academic_folder["item"].append({"name": "Attendance", "item": [
        create_request("Record Present", "POST", "{{baseUrl}}/api/teacher/attendance/record/", {"student_id": 1, "course_allocation_id": 1, "date": "2026-01-20", "status": "present"}),
        create_request("Record Excused", "POST", "{{baseUrl}}/api/teacher/attendance/record/", {"student_id": 1, "course_allocation_id": 1, "date": "2026-01-21", "status": "excused", "note": "Sick"}),
    ]})
    academic_folder["item"].append({"name": "Learning Content", "item": [
        create_request("List Materials", "GET", "{{baseUrl}}/api/teacher/learning-materials/"),
        create_request("Upload Document", "POST", "{{baseUrl}}/api/teacher/learning-materials/", 
                       {"title": "Lesson 1", "course": 1, "classroom": 1, "academic_year": 1, "file_url": "s3://path/to/file.pdf"}),
        create_request("Create Lesson Plan", "POST", "{{baseUrl}}/api/teacher/lesson-plans/", 
                       {"title": "Intro to Algebra", "course": 1, "classroom": 1, "academic_year": 1, "content": "Procedure...", "objectives": "Learn X", "date_planned": "2026-01-25"}),
    ]})
    collection["item"].append(academic_folder)

    # --- 07. Student & Guardian ---
    sg_folder = {"name": "07. Student & Guardian", "item": []}
    sg_folder["item"].append({"name": "Registration & Enrollment", "item": [
        create_request("Register Student", "POST", "{{baseUrl}}/api/manager/students/create/", 
                       {"email": "stu@school.com", "full_name": "Student Boy", "password": "pass", "school_id": 1, "grade_id": 1, "student_id": "STU001", "date_of_birth": "2010-01-01"}),
        create_request("Assign to Classroom", "POST", "{{baseUrl}}/api/manager/students/enrollments/create/", {"student_id": 1, "class_room_id": 1, "academic_year_id": 1}),
    ]})
    sg_folder["item"].append({"name": "Guardian Linkage (SRS FR-UM-004)", "item": [
        create_request("Create Guardian", "POST", "{{baseUrl}}/api/guardian/guardians/create/", {"email": "dad@guard.com", "full_name": "Father John", "password": "pass", "school_id": 1}),
        create_request("Link to Child", "POST", "{{baseUrl}}/api/guardian/guardians/{{guardianId}}/link-student/", {"student_id": 1, "relationship_type": "father"}),
        create_request("Deactivate Link", "POST", "{{baseUrl}}/api/guardian/student-links/{{enrollmentId}}/deactivate/"),
    ]})
    collection["item"].append(sg_folder)

    # --- 08. Communications ---
    comm_folder = {"name": "08. Communications", "item": []}
    comm_folder["item"].append({"name": "Direct Messaging", "item": [
        create_request("Inbox", "GET", "{{baseUrl}}/api/user-messages/"),
        create_request("Send Message", "POST", "{{baseUrl}}/api/user-messages/", {"recipient_ids": [1], "subject": "Question", "body": "Hello teacher"}),
        create_request("View Thread", "GET", "{{baseUrl}}/api/user-messages/thread/{{threadId}}/"),
        create_request("Mark Message Read", "POST", "{{baseUrl}}/api/user-messages/{{messageId}}/read/"),
    ]})
    comm_folder["item"].append({"name": "System Notifications", "item": [
        create_request("My Notifications", "GET", "{{baseUrl}}/api/notifications/"),
        create_request("Mark Notify Read", "POST", "{{baseUrl}}/api/notifications/{{notificationId}}/mark-read/"),
        create_request("404 Notify Detail", "GET", "{{baseUrl}}/api/notifications/9999/"),
    ]})
    collection["item"].append(comm_folder)

    # --- 09. Reports & Exports (SRS RA) ---
    report_folder = {"name": "09. Reports & Exports", "item": [
        create_request("Dashboard Analytics", "GET", "{{baseUrl}}/api/statistics/dashboard/"),
        create_request("Workstream Performance", "GET", "{{baseUrl}}/api/statistics/workstream/{{workstreamId}}/"),
        create_request("Export Excel (Student List)", "POST", "{{baseUrl}}/api/reports/export/", {"report_type": "student_list", "export_format": "excel"}),
        create_request("Export PDF (Attendance)", "POST", "{{baseUrl}}/api/reports/export/", {"report_type": "attendance", "export_format": "pdf"}),
        create_request("Export CSV (Marks)", "POST", "{{baseUrl}}/api/reports/export/", {"report_type": "marks", "export_format": "csv"}),
    ]}
    collection["item"].append(report_folder)

    # --- 99. Failure & Edge Cases ---
    failure_folder = {"name": "99. Failure & Edge Cases", "item": [
        create_request("401 - Missing Token", "GET", "{{baseUrl}}/api/users/", header=[]),
        create_request("403 - Expired/Invalid Role", "POST", "{{baseUrl}}/api/school/create/", {"school_name": "No Access"}),
        create_request("404 - Invalid Academic Year", "GET", "{{baseUrl}}/api/academic-years/999/"),
        create_request("400 - Dupe User Email", "POST", "{{baseUrl}}/api/users/create/", {"email": "admin@test.com", "full_name": "X", "password": "p", "role": "admin"}),
    ]}
    collection["item"].append(failure_folder)

    with open('postman_collection.json', 'w') as f:
        json.dump(collection, f, indent=4)
    print("Postman collection generated: postman_collection.json")

if __name__ == "__main__":
    generate_postman_collection()
