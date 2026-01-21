from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import CustomUser, Role, SystemConfiguration
from workstream.models import WorkStream
from school.models import School
from datetime import date

class SystemConfigApiTests(APITestCase):
    def setUp(self):
        # Create users and entities
        self.admin = CustomUser.objects.create_user(email='admin@test.com', password='password123', role=Role.ADMIN, full_name='Admin')
        
        self.ws = WorkStream.objects.create(workstream_name="WS1", capacity=100)
        self.ws_manager = CustomUser.objects.create_user(email='ws_mgr@test.com', password='password123', role=Role.MANAGER_WORKSTREAM, full_name='WS Mgr', work_stream=self.ws)
        
        self.school = School.objects.create(school_name="School1", work_stream=self.ws)
        self.school_manager = CustomUser.objects.create_user(email='sch_mgr@test.com', password='password123', role=Role.MANAGER_SCHOOL, full_name='Sch Mgr', school=self.school)
        
        self.teacher = CustomUser.objects.create_user(email='teacher@test.com', password='password123', role=Role.TEACHER, full_name='Teacher')

        self.url_list = reverse('system-config-list')

    def test_admin_create_global_config(self):
        self.client.force_authenticate(user=self.admin)
        data = {'config_key': 'GLOBAL_SETTING', 'config_value': 'TRUE'}
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data['school'])
        self.assertIsNone(response.data['work_stream'])

    def test_ws_manager_create_config(self):
        self.client.force_authenticate(user=self.ws_manager)
        data = {'config_key': 'WS_SETTING', 'config_value': '100'}
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['work_stream'], self.ws.id)
        self.assertIsNone(response.data['school'])

    def test_school_manager_create_config(self):
        self.client.force_authenticate(user=self.school_manager)
        data = {'config_key': 'SCHOOL_SETTING', 'config_value': 'DARK_MODE'}
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['school'], self.school.id)
        self.assertTrue(SystemConfiguration.objects.filter(school=self.school, config_key='SCHOOL_SETTING').exists())

    def test_ws_manager_cannot_create_school_config(self):
        # WS manager should allow WS config creation, but passing school param via generic create is restricted by perform_create logic
        self.client.force_authenticate(user=self.ws_manager)
        data = {'config_key': 'BAD_CONFIG', 'config_value': 'X', 'school': self.school.id}
        # The view logic forces work_stream=user.work_stream and ignores/validates against school?
        # My implementation: perform_create sets work_stream. validatator checks both not set.
        # If I convert my Validator to not raise if one is ignored? The view raises ValidationError explicitly.
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_visibility(self):
        # Setup configs
        SystemConfiguration.objects.create(config_key='GLOBAL', config_value='G', work_stream=None, school=None)
        SystemConfiguration.objects.create(config_key='WS1_CONF', config_value='W', work_stream=self.ws, school=None)
        SystemConfiguration.objects.create(config_key='SCH1_CONF', config_value='S', work_stream=None, school=self.school) # Wait, school configs usually don't have work_stream set? View logic assumes school.work_stream relation for query.
        
        # Admin sees all 3
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(self.url_list)
        self.assertEqual(res.data['count'], 3)

        # WS Manager sees Global + WS1 + SCH1 (as per logic: Q(school__work_stream=user.work_stream))
        self.client.force_authenticate(user=self.ws_manager)
        res = self.client.get(self.url_list)
        self.assertEqual(res.data['count'], 3)

        # School Manager sees Global + WS1 + SCH1
        self.client.force_authenticate(user=self.school_manager)
        res = self.client.get(self.url_list)
        self.assertEqual(res.data['count'], 3)

        # Teacher sees 0
        self.client.force_authenticate(user=self.teacher)
        res = self.client.get(self.url_list)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
