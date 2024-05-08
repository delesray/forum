import unittest
from unittest.mock import patch
from data.models.user import UserInfo, UserUpdate, User, UserRegister
from services import users_services as users
from services.users_services import IntegrityError
from tests.test_utils import EMAIL, FIRST_NAME, LAST_NAME, USER_ID, USERNAME, PASSWORD, create_user, create_user_info


username1, username2, username3 = 'user1', 'user2', 'user3'


class UsersServices_Should(unittest.TestCase):

    def test_getAll_returnsListOfUserInfoObjects_ifUsers(self):
        with patch('services.users_services.read_query') as mock_get_all_users:

            mock_get_all_users.return_value = [(username1, EMAIL, FIRST_NAME, LAST_NAME),
                                               (username2, EMAIL,
                                                FIRST_NAME, LAST_NAME),
                                               (username3, EMAIL, FIRST_NAME, LAST_NAME)]

            expected = [create_user_info(username1),
                        create_user_info(username2),
                        create_user_info(username3)]

            actual = users.get_all()

            self.assertEqual(expected, actual)

    def test_getAll_returnsEmptyList_ifNotUsers(self):
        with patch('services.users_services.read_query') as mock_get_all_users:
            mock_get_all_users.return_value = []
            expected = []

            actual = users.get_all()

            self.assertEqual(expected, actual)

    def test_getById_returnsUserInfoObject_ifUser(self):
        with patch('services.users_services.read_query') as mock_get_user:
            mock_get_user.return_value = [
                (username1, EMAIL, FIRST_NAME, LAST_NAME)]
            expected = create_user_info(username1)

            actual = users.get_by_id(user_id=USER_ID)

            self.assertEqual(expected, actual)

    def test_getById_returnsNone_ifNotUser(self):
        with patch('services.users_services.read_query') as mock_get_user:
            mock_get_user.return_value = []
            expected = None

            actual = users.get_by_id(user_id=USER_ID)

            self.assertEqual(expected, actual)

    def test_findByUsername_returnsUser_ifUser(self):
        with patch('services.users_services.read_query') as mock_find_by_name:
            mock_find_by_name.return_value = [
                (USER_ID, USERNAME, PASSWORD, EMAIL, FIRST_NAME, LAST_NAME, False)]
            expected = create_user()

            actual = users.find_by_username(username=USERNAME)

            self.assertEqual(expected, actual)

    def test_findByUsername_returnsNone_ifNotUser(self):
        with patch('services.users_services.read_query') as mock_find_by_name:
            mock_find_by_name.return_value = []
            expected = None

            actual = users.find_by_username(username=USERNAME)

            self.assertEqual(expected, actual)

    def test_registerReturnsUser_ifSuccessful(self):
        with patch('services.users_services.hash_pass') as mock_hash_pass, \
                patch('services.users_services.insert_query') as mock_register_user:

            mock_hash_pass.return_value = PASSWORD
            mock_register_user.return_value = USER_ID
            expected = USER_ID

            actual = users.register(user=UserRegister(username=USERNAME,
                                                      password=PASSWORD,
                                                      email=EMAIL,
                                                      first_name=FIRST_NAME,
                                                      last_name=LAST_NAME))

            self.assertEqual(expected, actual)

    def test_registerReturnsIntegrityError_ifRaised(self):
        with patch('services.users_services.hash_pass') as mock_hash_pass, \
                patch('services.users_services.insert_query') as mock_register_user:

            mock_hash_pass.return_value = PASSWORD
            mock_register_user.side_effect = IntegrityError

            result = users.register(user=UserRegister(username=USERNAME,
                                                      password=PASSWORD,
                                                      email=EMAIL,
                                                      first_name=FIRST_NAME,
                                                      last_name=LAST_NAME))
            self.assertIsInstance(result, IntegrityError)

    def test_tryLogin_returnsUser_ifUserAndPass(self):
        with patch('services.users_services.find_by_username') as mock_find_user, \
                patch('services.users_services.verify_password') as mock_verify_pass:

            user = create_user()
            mock_find_user.return_value = user
            mock_verify_pass.return_value = True
            excepted = user

            actual = users.try_login(
                username=user.username, password=user.password)

            self.assertEqual(excepted, actual)

    def test_tryLogin_returnsNone_ifNotUser(self):
        with patch('services.users_services.find_by_username') as mock_find_user:

            user = create_user()
            mock_find_user.return_value = None
            excepted = None

            actual = users.try_login(
                username=user.username, password=user.password)

            self.assertEqual(excepted, actual)

    def test_tryLogin_returnsNone_ifUserAndNotPass(self):
        with patch('services.users_services.find_by_username') as mock_find_user, \
                patch('services.users_services.verify_password') as mock_verify_pass:

            user = create_user()
            mock_find_user.return_value = user
            mock_verify_pass.return_value = False
            excepted = None

            actual = users.try_login(
                username=user.username, password=user.password)

            self.assertEqual(excepted, actual)

    def test_updateReturnsUserUpdateObject_ifUpdates(self):
        with patch('services.users_services.update_query') as mock_update:
            mock_update.return_value = True
            user = create_user()
            edited_user = UserUpdate(first_name='newname')
            expected = UserUpdate(first_name=edited_user.first_name,
                                  last_name=user.last_name)

            actual = users.update(old=user, new=edited_user)

            self.assertEqual(expected, actual)

    def test_updateReturnsUserUpdateObject_ifNotUpdates(self):
        with patch('services.users_services.update_query') as mock_update:
            mock_update.return_value = True
            user = create_user()
            edited_user = UserUpdate()
            expected = UserUpdate(first_name=user.first_name,
                                  last_name=user.last_name)

            actual = users.update(old=user, new=edited_user)

            self.assertEqual(expected, actual)
