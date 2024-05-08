from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock
from data.models.topic import TopicResponse
from common.utils import PaginationInfo, Links
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


class TST:
    page = 2
    size = 3
    # category_topics_paginate = r.CategoryTopicsPaginate(
    #     category=CAT1.OBJ,
    #     topics=None,  # list[TopicsResponse]
    #     pagination_info=None,  # PaginationInfo obj ?
    #     links=None  # Links obj ?
    # )


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


class CategoryRouter_Should(TestCase):
    def setUp(self) -> None:
        mock_category_services.reset_mock()
        mock_category_services.reset_mock()

    # get_all_categories
    def test_get_all_categories_returns_list_of_categories(self):
        mock_category_services.get_all = lambda search: [CAT1.OBJ, CAT2.OBJ]
        expected = [CAT1.OBJ, CAT2.OBJ]

        result = r.get_all_categories(search=None)
        self.assertEqual(expected, result)

    # get_category_by_id
    #   v1 raises_HTTPException_SC_NotFound
    def test_v1_get_category_by_id_raises_HTTPException_SC_NotFound(self):
        mock_category_services.get_by_id = lambda category_id: None
        # mock_category_services.get_by_id.return_value = None

        with self.assertRaises(r.HTTPException):
            r.get_category_by_id(CAT1.ID, Mock(), Mock())

    #   v2 raises_HTTPException_SC_NotFound
    @patch('routers.categories.categories_services')
    def test_v2_get_category_by_id_raises_HTTPException_SC_NotFound(self, mock_services):
        mock_services.get_by_id.return_value = None

        with self.assertRaises(r.HTTPException) as e:
            r.get_category_by_id(CAT1.ID, Mock(), Mock())

        self.assertEqual(r.SC.NotFound, e.exception.status_code)

    def test_get_category_by_id_raises_HTTPException_cat_private_and_no_user(self):
        #   42-44
        private_category_mock = Mock(is_private=True)
        mock_category_services.get_by_id = lambda category_id: private_category_mock
        anonymous_user = r.AnonymousUser()

        with self.assertRaises(r.HTTPException) as e:
            r.get_category_by_id(CAT1.ID, anonymous_user, Mock())

        self.assertEqual(r.SC.Unauthorized, e.exception.status_code)

    def test_get_category_by_id_raises_HTTPException_if_cat_private_and_user_NO_permission(self):
        #   46-51
        test_user = Mock(is_admin=False)
        private_category_mock = Mock(is_private=True)
        mock_category_services.get_by_id = lambda category_id: private_category_mock
        mock_category_services.has_access_to_private_category = lambda x, y: False

        with self.assertRaises(r.HTTPException) as e:
            r.get_category_by_id(CAT1.ID, test_user, Mock())

        self.assertEqual(r.SC.Forbidden, e.exception.status_code)

    def test_get_category_by_id_raises_HTTPException_if_cat_private_and_user_HAS_permission(self):
        #   53-
        test_user = Mock(is_admin=False)
        private_category_mock = Mock(is_private=True)
        mock_category_services.get_by_id = lambda category_id: private_category_mock
        mock_category_services.has_access_to_private_category = lambda x, y: True

        mock_topic_services.get_all = lambda p, s: None, None

        with self.assertRaises(r.HTTPException) as e:
            r.get_category_by_id(CAT1.ID, test_user, Mock())

        self.assertEqual(r.SC.Forbidden, e.exception.status_code)

    @patch('routers.categories.get_pagination_info')
    @patch('routers.categories.create_links')
    def test_get_category_by_id_HappyCase_correct_CategoryTopicsPaginate(  # name ?
            self, mock_create_links, mock_get_pagination_info
    ):
        public_category_mock = Mock(spec=r.Category, is_private=False)
        public_category_mock.name = CAT1.NAME
        guest_user = Mock()  # AnonymousUser ?

        # mock_category_services.get_by_id = lambda category_id: public_category_mock
        topics = [Mock(spec=TopicResponse) for _ in range(2)]  # Mock list of 2 topics

        # mock_topic_services.get_all = \
        #     lambda page, size, sort, sort_by, search, category=2: (topics, 10)  # Return topics and total count

        mock_get_pagination_info.return_value = Mock(spec=PaginationInfo)  # ?
        mock_create_links.return_value = Mock(spec=Links)  # ?

        mock_category_services.f = lambda request, page, size, sort, sort_by, search, category: \
            (topics, mock_get_pagination_info.return_value, mock_create_links.return_value)

        expected = {
            'category': public_category_mock,
            'topics': topics,
            'pagination_info': mock_get_pagination_info.return_value,
            'links': mock_create_links.return_value,
        }
        result = r.get_category_by_id(
            category_id=CAT1.ID, current_user=guest_user,
            request=Mock())  # page=TST.page, size=TST.size ?

        self.assertEqual(expected['category'], result.category)
        self.assertEqual(expected['category'], result.category)
        self.assertIsInstance(result.category, r.Category)
