
# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** EduTraker
- **Date:** 2026-01-17
- **Prepared by:** TestSprite AI Team

---

## 2️⃣ Requirement Validation Summary

#### Test TC001 get public workstream info
- **Test Code:** [TC001_get_public_workstream_info.py](./TC001_get_public_workstream_info.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cda936b9-ec4b-4c48-8369-6f7b9f0f718a/a2ae2580-3a11-46ff-9106-1a3bdbd67a93
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC002 list all workstreams with filters
- **Test Code:** [TC002_list_all_workstreams_with_filters.py](./TC002_list_all_workstreams_with_filters.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 110, in <module>
  File "<string>", line 47, in test_list_all_workstreams_with_filters
  File "<string>", line 19, in create_workstream
  File "/var/task/requests/models.py", line 1024, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 404 Client Error: Not Found for url: http://localhost:8000/api/workstream/

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cda936b9-ec4b-4c48-8369-6f7b9f0f718a/b14c08bc-9eda-46aa-bcac-89a6c4372447
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC003 create new workstream with validation
- **Test Code:** [TC003_create_new_workstream_with_validation.py](./TC003_create_new_workstream_with_validation.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 133, in <module>
  File "<string>", line 49, in test_create_new_workstream_with_validation
AssertionError: Unexpected status code 400 for valid create

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cda936b9-ec4b-4c48-8369-6f7b9f0f718a/0f32f468-4ab7-4e98-bce2-d2b1fafa770d
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC004 update existing workstream partially
- **Test Code:** [TC004_update_existing_workstream_partially.py](./TC004_update_existing_workstream_partially.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 67, in <module>
  File "<string>", line 20, in test_update_existing_workstream_partially
AssertionError: Workstream creation failed with status 404

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cda936b9-ec4b-4c48-8369-6f7b9f0f718a/ccd5fc15-44c0-40db-969b-c9f5c68802e6
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC005 deactivate workstream without deletion
- **Test Code:** [TC005_deactivate_workstream_without_deletion.py](./TC005_deactivate_workstream_without_deletion.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 83, in <module>
  File "<string>", line 28, in test_deactivate_workstream_without_deletion
AssertionError: Failed to create workstream for test setup: 404 {"detail":"No CustomUser matches the given query."}

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/cda936b9-ec4b-4c48-8369-6f7b9f0f718a/c68bb353-7280-4686-ba54-40f69cc6eef2
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---


## 3️⃣ Coverage & Matching Metrics

- **20.00** of tests passed

| Requirement        | Total Tests | ✅ Passed | ❌ Failed  |
|--------------------|-------------|-----------|------------|
| ...                | ...         | ...       | ...        |
---


## 4️⃣ Key Gaps / Risks
{AI_GNERATED_KET_GAPS_AND_RISKS}
---