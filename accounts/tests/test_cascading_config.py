from rest_framework.test import APITestCase
from accounts.models import SystemConfiguration, CustomUser, Role
from workstream.models import WorkStream
from school.models import School
from accounts.selectors.configuration_selectors import config_get_value

class CascadingConfigTests(APITestCase):
    def setUp(self):
        self.ws = WorkStream.objects.create(workstream_name="WS1", capacity=10)
        self.school = School.objects.create(school_name="Sch1", work_stream=self.ws)
        
    def test_cascading_priority(self):
        # 1. Global
        SystemConfiguration.objects.create(config_key="GRADING", config_value="GLOBAL")
        self.assertEqual(config_get_value("GRADING"), "GLOBAL")
        self.assertEqual(config_get_value("GRADING", school=self.school), "GLOBAL")
        
        # 2. Workstream override
        SystemConfiguration.objects.create(config_key="GRADING", config_value="WS", work_stream=self.ws)
        self.assertEqual(config_get_value("GRADING", work_stream=self.ws), "WS")
        self.assertEqual(config_get_value("GRADING", school=self.school), "WS")
        
        # 3. School override
        SystemConfiguration.objects.create(config_key="GRADING", config_value="SCH", school=self.school)
        self.assertEqual(config_get_value("GRADING", school=self.school), "SCH")
        
        # Global should still be GLOBAL if requested without context
        self.assertEqual(config_get_value("GRADING"), "GLOBAL")
