from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock

import routers.categories
from routers import categories as r

WRITE_ACCESS = 1
USER_ID, USERNAME = 1, 'username'
COUNT_1, COUNT_0 = 1, 0


class CAT1:
    ID = 1
    NAME = 'test_name'
    LOCKED = False
    PRIVATE = False
    VALUES_TUPLE = (ID, NAME, LOCKED, PRIVATE)
    OBJ = r.Category.from_query(*VALUES_TUPLE)


class CAT2:
    ID = 2
    NAME = 'test_name2'
    LOCKED = True
    PRIVATE = True
    VALUES_TUPLE = (ID, NAME, LOCKED, PRIVATE)
    OBJ = r.Category.from_query(*VALUES_TUPLE)


mock_category_services = Mock(spec='routers.categories.categories_services')
mock_topic_services = Mock(spec='routers.categories.topics_services')
routers.categories.categories_services = mock_category_services
routers.categories.topics_services = mock_topic_services


# @patch('routers.categories.OptionalUser', return_value=)
class CategoryRouter_Should(TestCase):
    def setUp(self) -> None:
        mock_category_services.reset_mock()
        mock_topic_services.reset_mock()

    # get_all_categories
    @patch('routers.categories.categories_services.get_all')
    def test_get_all_categories_returns_list_of_categories(self, mock_get_all):
        mock_get_all.return_value = [CAT1.OBJ, CAT2.OBJ]
        expected = [CAT1.OBJ, CAT2.OBJ]

        result = r.get_all_categories()
        self.assertEqual(expected, result)

    # get_category_by_id
    #   v1
    def test_v1_get_category_by_id_raises_HTTPException_SC_NotFound(self):
        mock_category_services.get_by_id = lambda x=CAT1.ID: None  # x = 'not_obligatory'

        with self.assertRaises(r.HTTPException):
            r.get_category_by_id(CAT1.ID, Mock(), Mock())

    #   v2
    @patch('routers.categories.categories_services')
    def test_v2_get_category_by_id_raises_HTTPException_SC_NotFound(self, mock_services):
        mock_services.get_by_id.return_value = None

        with self.assertRaises(r.HTTPException):
            r.get_category_by_id(CAT1.ID, Mock(), Mock())
