from unittest import TestCase
from unittest.mock import patch, Mock
from data.models.category import Category
from services import categories_services as s
from services.categories_services import IntegrityError

CAT1_ID = 1
CAT1_NAME = 'test'
CAT1_LOCKED = False
CAT1_PRIVATE = False
CAT1_VALUES_TUPLE = (CAT1_ID, CAT1_NAME, CAT1_LOCKED, CAT1_PRIVATE)
CAT1_OBJ = Category.from_query(*CAT1_VALUES_TUPLE)

CAT2_VALUES_TUPLE2 = (2, 'test2', True, True)

WRITE_ACCESS = 1

USER_ID, USERNAME = 1, 'username'
COUNT_1, COUNT_0 = 1, 0

read_query_path = 'services.categories_services.read_query'
update_query_path = 'services.categories_services.update_query'
insert_query_path = 'services.categories_services.insert_query'


class CategoriesServices_Should(TestCase):
    # exists_by_name
    @patch(read_query_path)
    def test_exists_by_name_returns_True_when_exists(self, mock_read_query):
        mock_read_query.return_value = [(1,)]
        result = s.exists_by_name(CAT1_NAME)
        self.assertTrue(result)

    @patch(read_query_path)
    def test_exists_by_name_returns_False_when_exists(self, mock_read_query):
        mock_read_query.return_value = []
        result = s.exists_by_name(CAT1_NAME)
        self.assertFalse(result)

    # get_all
    @patch(read_query_path)
    def test_get_all_returns_list_of_categories(self, mock_read_query):
        mock_read_query.return_value = [CAT1_VALUES_TUPLE, CAT2_VALUES_TUPLE2]
        expected = [Category.from_query(*row) for row in mock_read_query.return_value]

        result = s.get_all()
        self.assertEqual(expected, result)

    @patch(read_query_path)
    def test_get_all_returns_empty_list_when_no_categories(self, mock_read_query):
        mock_read_query.return_value = []
        expected = []

        result = s.get_all()
        self.assertEqual(expected, result)

    # get_by_id
    @patch(read_query_path)
    def test_get_by_id_returns_correct_object_with_correct_values(self, mock_read_query):
        mock_read_query.return_value = [CAT1_VALUES_TUPLE]
        expected = Category.from_query(*CAT1_VALUES_TUPLE)

        result = s.get_by_id(CAT1_ID)

        self.assertEqual(expected, result)

    @patch(read_query_path)
    def test_get_by_id_returns_None_when_empty(self, mock_read_query):
        mock_read_query.return_value = []
        result = s.get_by_id(CAT1_ID)
        self.assertIsNone(result)

    # create
    @patch(insert_query_path)
    def test_create_returns_IntegrityError_when_db_level_violation(self, mock_insert_query):
        mock_insert_query.side_effect = IntegrityError
        result = s.create(CAT1_OBJ)
        self.assertIsInstance(result, IntegrityError)

    @patch(insert_query_path)
    def test_create_returns_correct_Category_obj(self, mock_insert_query):
        mock_insert_query.return_value = CAT1_ID
        expected = CAT1_OBJ

        CAT1_OBJ.category_id = None
        result = s.create(CAT1_OBJ)
        self.assertEqual(expected, result)

    # get_user_access_level
    @patch(read_query_path)
    def test_get_user_access_level_returns_None(self, mock_read_query):
        mock_read_query.return_value = []
        result = s.get_user_access_level(USER_ID, CAT1_ID)
        self.assertIsNone(result)

    @patch(read_query_path)
    def test_get_user_access_level_returns_True(self, mock_read_query):
        mock_read_query.return_value = [(WRITE_ACCESS,)]
        result = s.get_user_access_level(USER_ID, CAT1_ID)
        self.assertTrue(result)

    # update_privacy
    @patch(update_query_path)
    def test_update_privacy_update_query_used_once(self, mock_update_query):
        mock_update_query.return_value = None
        s.update_privacy(not CAT1_PRIVATE, CAT1_ID)
        mock_update_query.assert_called_once_with(
            'UPDATE categories SET is_private = ? WHERE category_id = ?',
            (not CAT1_PRIVATE, CAT1_ID,)
        )

    # is_user_in
    @patch(read_query_path)
    def test_is_user_in_returns_True(self, mock_read_query):
        mock_read_query.return_value = [[COUNT_1, ]]
        result = s.is_user_in(USER_ID, CAT1_ID)
        self.assertTrue(result)

    @patch(read_query_path)
    def test_is_user_in_returns_False(self, mock_read_query):
        mock_read_query.return_value = [[COUNT_0, ]]
        result = s.is_user_in(USER_ID, CAT1_ID)
        self.assertFalse(result)

    # add_user
    @patch(insert_query_path)
    def test_update_add_user_insert_query_used_once(self, mock_insert_query):
        mock_insert_query.return_value = None
        s.add_user(USER_ID, CAT1_ID)
        mock_insert_query.assert_called_once_with(
            'INSERT INTO users_categories_permissions(user_id,category_id) VALUES(?,?)',
            (USER_ID, CAT1_ID,)
        )

    # get_privileged_users
    @patch(read_query_path)
    def test_get_privileged_users_returns_list_of_tuples(self, mock_read_query):
        mock_read_query.return_value = [(USER_ID, USERNAME, WRITE_ACCESS)]

        result = s.get_privileged_users(CAT1_ID)
        self.assertEqual(type(result), list)
        self.assertTrue(all(type(x) is tuple for x in result))
