from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock
from data.models.topic import TopicResponse
from common.utils import PaginationInfo, Links
from routers import admin as r

global_admin_mock = Mock(is_admin=True)
dummy_string = 'dummy'


class MyClass:
    def __init__(self):
        self.atr1 = 1
        self.atr2 = 2


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
