
# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** EduTraker
- **Date:** 2026-01-12
- **Prepared by:** TestSprite AI Team

---

## 2️⃣ Requirement Validation Summary

#### Test TC001 test_jwt_token_refresh
- **Test Code:** [TC001_test_jwt_token_refresh.py](./TC001_test_jwt_token_refresh.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/50267c09-6a28-4782-8f61-60b3ef67d65c/9e8e8dc9-2991-4fbf-83fb-105c8ad25c1e
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC002 test_portal_user_login
- **Test Code:** [TC002_test_portal_user_login.py](./TC002_test_portal_user_login.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/50267c09-6a28-4782-8f61-60b3ef67d65c/d22b4c46-4fe3-40e7-9519-ab2df5db29fb
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC003 test_portal_user_registration
- **Test Code:** [TC003_test_portal_user_registration.py](./TC003_test_portal_user_registration.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/50267c09-6a28-4782-8f61-60b3ef67d65c/16c95687-1976-484a-8127-02b7513e0d6e
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC004 test_workstream_user_login
- **Test Code:** [TC004_test_workstream_user_login.py](./TC004_test_workstream_user_login.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 143, in <module>
  File "<string>", line 79, in test_workstream_user_login
  File "/var/task/requests/models.py", line 1024, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 400 Client Error: Bad Request for url: http://localhost:8000/api/workstream/

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/50267c09-6a28-4782-8f61-60b3ef67d65c/770aef1b-5347-4be6-8c8a-b3a81fe76ba0
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC005 test_workstream_user_registration
- **Test Code:** [TC005_test_workstream_user_registration.py](./TC005_test_workstream_user_registration.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/50267c09-6a28-4782-8f61-60b3ef67d65c/3420d111-08cd-41d9-96bb-381e14170b1f
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC006 test_user_creation_with_role_validation
- **Test Code:** [TC006_test_user_creation_with_role_validation.py](./TC006_test_user_creation_with_role_validation.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 84, in <module>
  File "<string>", line 51, in test_user_creation_with_role_validation
AssertionError: Expected 201 or 200, got 400

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/50267c09-6a28-4782-8f61-60b3ef67d65c/f0106df1-9dde-47c5-94a0-e6a01fa12272
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC007 test_user_activation
- **Test Code:** [TC007_test_user_activation.py](./TC007_test_user_activation.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 51, in <module>
  File "<string>", line 29, in test_user_activation
AssertionError: User creation failed: {"email":"A user with this email already exists."}

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/50267c09-6a28-4782-8f61-60b3ef67d65c/03daef4e-c285-4fb8-b1b6-76ae8a181ffb
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC008 test_workstream_creation
- **Test Code:** [TC008_test_workstream_creation.py](./TC008_test_workstream_creation.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/50267c09-6a28-4782-8f61-60b3ef67d65c/4d3ddefd-3faa-4009-8ce2-fb32137af74c
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC009 test_school_creation_with_manager_validation
- **Test Code:** [TC009_test_school_creation_with_manager_validation.py](./TC009_test_school_creation_with_manager_validation.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 179, in <module>
  File "<string>", line 128, in test_school_creation_with_manager_validation
  File "<string>", line 88, in create_school
  File "/var/task/requests/models.py", line 1024, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 400 Client Error: Bad Request for url: http://localhost:8000/api/manager/schools/create/

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/50267c09-6a28-4782-8f61-60b3ef67d65c/c2c936a7-cb21-4f7f-963e-08e7e566e684
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC010 test_academic_year_creation
- **Test Code:** [TC010_test_academic_year_creation.py](./TC010_test_academic_year_creation.py)
- **Test Error:** Traceback (most recent call last):
  File "<string>", line 47, in test_academic_year_creation
AssertionError

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 180, in <module>
  File "<string>", line 50, in test_academic_year_creation
AssertionError: Manager Workstream user creation failed: 

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/50267c09-6a28-4782-8f61-60b3ef67d65c/847905ab-a8e2-489c-9a8f-7c4a9aa3cf4c
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---


## 3️⃣ Coverage & Matching Metrics

- **50.00** of tests passed

| Requirement        | Total Tests | ✅ Passed | ❌ Failed  |
|--------------------|-------------|-----------|------------|
| ...                | ...         | ...       | ...        |
---


## 4️⃣ Key Gaps / Risks
{AI_GNERATED_KET_GAPS_AND_RISKS}
---