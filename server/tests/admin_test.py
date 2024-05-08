from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock
from data.models.topic import TopicResponse
from common.utils import PaginationInfo, Links
from routers import admin as r

global_admin_mock = Mock(is_admin=True)
dummy_string = 'dummy'


class AdminRouter_Should(TestCase):
    @patch('routers.admin.categories_services.create')
    def test_create_category_raises_BadRequest(self, mock_create):
        mock_create.return_value = Mock(
            spec=r.categories_services.IntegrityError, msg=dummy_string)

        with self.assertRaises(r.HTTPBaRequest):
            r.create_category(Mock(), global_admin_mock)

    @patch('routers.admin.categories_services.get_by_id')
    def test_switch_category_privacy_raises_NotFound(self, mock_get_by_id):
        mock_get_by_id.return_value = None

        with self.assertRaises(r.HTTPNotFound):
            r.switch_category_privacy(Mock(), global_admin_mock)

    @patch('routers.admin.categories_services.update_privacy')
    @patch('routers.admin.categories_services.get_by_id')
    def test_switch_category_privacy_raises_HappyCase_update_called(
            self, mock_get_by_id, mock_update_privacy):
        mock_get_by_id.return_value = Mock(spec=r.Category, is_private=True)
        mock_get_by_id.return_value.name = dummy_string
        r.switch_category_privacy(Mock(), global_admin_mock)

        mock_update_privacy.assert_called_once()

    @patch('routers.admin.users_services.get_by_id')
    def test_give_user_category_read_access_raises_NotFound_when_no_user(self, mock_get_by_id):
        mock_get_by_id.return_value = None

        with self.assertRaises(r.HTTPNotFound):
            r.give_user_category_read_access(Mock(), Mock(), global_admin_mock)

    @patch('routers.admin.categories_services.get_by_id')
    @patch('routers.admin.users_services.get_by_id')
    def test_give_user_category_read_access_raises_NotFound_when_no_category(
            self, mock_get_by_id, mock_get_by_id_user):
        mock_get_by_id_user.return_value = None
        mock_get_by_id.return_value = None

        with self.assertRaises(r.HTTPNotFound):
            r.give_user_category_read_access(Mock(), Mock(), global_admin_mock)

    @patch('routers.admin.categories_services.is_user_in')
    @patch('routers.admin.categories_services.get_by_id')
    @patch('routers.admin.users_services.get_by_id')
    def test_give_user_category_read_access_raises_BadRequest_when_user_already_in(
            self, mock_get_by_id, mock_get_by_id_user, mock_is_user_in):
        mock_get_by_id_user.return_value = True
        mock_get_by_id.return_value = True
        mock_is_user_in.return_value = True

        with self.assertRaises(r.HTTPBaRequest):
            r.give_user_category_read_access(Mock(), Mock(), global_admin_mock)

    @patch('routers.admin.categories_services.add_user')
    @patch('routers.admin.categories_services.is_user_in')
    @patch('routers.admin.categories_services.get_by_id')
    @patch('routers.admin.users_services.get_by_id')
    def test_give_user_category_read_access_HappyCase(
            self, mock_get_by_id, mock_get_by_id_user, mock_is_user_in, mock_add_user):
        mock_get_by_id_user.return_value = True
        mock_get_by_id.return_value = True
        mock_is_user_in.return_value = False
        mock_add_user.return_value = None

        r.give_user_category_read_access(Mock(), Mock(), global_admin_mock)
        self.assertTrue(True)  # no Exceptions met so we return true

    @patch('routers.admin.categories_services.update_user_access_level')
    @patch('routers.admin.categories_services.get_by_id')
    @patch('routers.admin.users_services.get_by_id')
    def test_switch_user_category_write_access_HappyCase(
            self, mock_get_by_id, mock_get_by_id_user, mock_update_user_access_level):
        mock_get_by_id_user.return_value = True
        mock_get_by_id.return_value = True
        mock_update_user_access_level.return_value = True

        try:
            r.switch_user_category_write_access(Mock(), Mock(), global_admin_mock)
            self.assertTrue(True)  # if no exception is raised - valid
        except Exception as e:
            self.fail(f"Unexpected error raised: {e}")

    @patch('routers.admin.categories_services.get_by_id')
    def test_view_privileged_users_NotFound(
            self, mock_get_by_id, ):
        mock_get_by_id.return_value = None

        with self.assertRaises(r.HTTPNotFound):
            r.view_privileged_users(Mock(), global_admin_mock)

    @patch('routers.admin.categories_services.get_by_id')
    def test_view_privileged_users_Category_was_public(
            self, mock_get_by_id, ):
        mock_get_by_id.return_value = Mock(spec=r.Category, is_private=False)

        result = r.view_privileged_users(Mock(), global_admin_mock)
        self.assertIsNotNone(result)  # no Exceptions met so we return true

    @patch('routers.admin.categories_services.get_privileged_users')
    @patch('routers.admin.categories_services.get_by_id')
    def test_view_privileged_users_No_users_in_category(
            self, mock_get_by_id, mock_get_privileged_users):
        mock_get_by_id.return_value = Mock(spec=r.Category, is_private=True)
        mock_get_privileged_users.return_value = []

        result = r.view_privileged_users(Mock(), global_admin_mock)
        self.assertIsNotNone(result)  # no Exceptions met so we return true

    @patch('routers.admin.categories_services.response_obj_privileged_users')
    @patch('routers.admin.categories_services.get_privileged_users')
    @patch('routers.admin.categories_services.get_by_id')
    def test_view_privileged_users_HappyCase_final_return(
            self, mock_get_by_id, mock_get_privileged_users, mock_response_obj_privileged_users):
        mock_get_by_id.return_value = Mock(spec=r.Category, is_private=True)
        mock_get_privileged_users.return_value = [Mock()]
        mock_response_obj_privileged_users.return_value = True

        result = r.view_privileged_users(Mock(), global_admin_mock)
        self.assertIsNotNone(result)  # no Exceptions met so we return true
