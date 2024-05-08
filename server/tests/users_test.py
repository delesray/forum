import unittest
from unittest.mock import Mock, patch
from routers import users
from routers.users import HTTPException, OAuth2PasswordRequestForm
from tests.test_utils import create_user_info, create_user, USERNAME, PASSWORD, EMAIL, fake_token, USER_ID, fake_user
from data.models.user import UserDelete, UserRegister, UserUpdate, UserChangePassword


class UsersRouter_Should(unittest.TestCase):
    def test_registerUser_returnsSuccessMessage_ifUserRegistered(self):
        with patch('routers.users.users_services.register') as mock_register:

            user = create_user()
            registration_info = UserRegister(
                username=USERNAME, password=PASSWORD, email=EMAIL)
            mock_register.return_value = user.user_id
            expected = f"User with ID: {user.user_id} registered"

            actual = users.register_user(user=registration_info)

            self.assertEqual(expected, actual)

    def test_registerUser_raises400_ifIncorrectRegisterData(self):
        with patch('routers.users.users_services.register') as mock_register:

            fake_integrity_error = Mock()
            registration_info = UserRegister(
                username=USERNAME, password=PASSWORD, email=EMAIL)
            mock_register.side_effect = fake_integrity_error

            with self.assertRaises(HTTPException) as ex:
                users.register_user(user=registration_info)

                self.assertEqual(400, ex.exception.status_code)

    def test_loginReturnsToken_ifSuccessfulLogin(self):
        with patch('routers.users.users_services.try_login') as mock_try_login, \
                patch('routers.users.create_access_token') as mock_create_token:

            user = create_user()
            mock_try_login.return_value = user
            mock_create_token.return_value = fake_token
            expected = fake_token

            actual = users.login(form_data=OAuth2PasswordRequestForm(
                username=USERNAME, password=PASSWORD))

            self.assertEqual(expected, actual)

    def test_loginRaises401_ifIncorrectUsernameOrPassword(self):
        with patch('routers.users.users_services.try_login') as mock_try_login:

            mock_try_login.return_value = None

            with self.assertRaises(HTTPException) as ex:

                users.login(form_data=OAuth2PasswordRequestForm(
                    username=USERNAME, password=PASSWORD))

                self.assertEqual(401, ex.exception.status_code)
                self.assertEqual("Invalid credentials", ex.exception.detail)

    def test_getAllUsers_returnsUsers(self):
        with patch('routers.users.users_services.get_all') as mock_get_all:

            mock_get_all.return_value = [
                create_user(), create_user(), create_user()]
            expected = [create_user(), create_user(), create_user()]

            actual = users.get_all_users()

            self.assertEqual(expected, actual)

    def test_getUserById_returnsUser_ifUser(self):
        with patch('routers.users.users_services.get_by_id') as mock_get_by_id:

            mock_get_by_id.return_value = create_user_info()
            expected = create_user_info()

            actual = users.get_user_by_id(user_id=USER_ID)

            self.assertEqual(expected, actual)

    def test_getUserById_raises404_ifNotUser(self):
        with patch('routers.users.users_services.get_by_id') as mock_get_by_id:

            mock_get_by_id.return_value = None

            with self.assertRaises(HTTPException) as ex:
                users.get_user_by_id(user_id=USER_ID)

                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual(f"User with ID: {USER_ID} does\'t exist!",
                                 ex.exception.detail)

    def test_updateUser_returnsUpdatedUser(self):
        with patch('routers.users.users_services.update') as mock_update:
            fake_updated_user = Mock(spec=UserUpdate)
            mock_update.return_value = fake_updated_user
            expected = fake_updated_user

            actual = users.update_user(
                user=fake_updated_user, existing_user=fake_user())

            self.assertEqual(expected, actual)

    def test_changeUserPassword_returnsSuccessMessage_ifSuccessful(self):
        with patch('routers.users.utils.verify_password') as mock_verify_pass, \
                patch('routers.users.utils.hash_pass') as mock_hash_pass, \
                patch('routers.users.users_services.change_password') as mock_change_pass:
            mock_verify_pass.return_value = True
            mock_hash_pass.return_value = PASSWORD
            mock_change_pass = True
            data = UserChangePassword(
                current_password='password', new_password='somepass', confirm_password='somepass')
            expected = 'Password changed successfully'

            actual = users.change_user_password(data, fake_user())

            self.assertEqual(expected, actual)

    def test_changeUserPassword_raises401_ifCurrentPassNotMatch(self):
        with patch('routers.users.utils.verify_password') as mock_verify_pass:
            mock_verify_pass.return_value = False
            data = Mock()

            with self.assertRaises(HTTPException) as ex:
                users.change_user_password(data, fake_user())

                self.assertEqual(401, ex.exception.status_code)
                self.assertEqual(
                    "Current password does not match", ex.exception.detail)

    def test_change_UserPassword_raises401_ifNewPasswordNotMatch(self):
        with patch('routers.users.utils.verify_password') as mock_verify_pass:
            mock_verify_pass.return_value = True
            data = UserChangePassword(
                current_password='password', new_password='somepass', confirm_password='pass')

            with self.assertRaises(HTTPException) as ex:
                users.change_user_password(data, fake_user())

                self.assertEqual(401, ex.exception.status_code)
                self.assertEqual("New password does not match",
                                 ex.exception.detail)

    def test_deleteReturnsNone_ifSuccess(self):
        with patch('routers.users.utils.verify_password') as mock_verify_pass, \
                patch('routers.users.users_services.delete') as mock_delete:
            mock_verify_pass.return_value = True
            mock_delete.return_value = True
            expected = None

            actual = users.delete_user_by_id(
                existing_user=fake_user(), body=UserDelete(current_password=PASSWORD))

            self.assertEqual(expected, actual)

    def test_delete_raises400_ifCurrentPasswordNotMatch(self):
        with patch('routers.users.utils.verify_password') as mock_verify_pass:
            mock_verify_pass.return_value = False

            with self.assertRaises(HTTPException) as ex:
                users.delete_user_by_id(existing_user=fake_user(
                ), body=UserDelete(current_password=PASSWORD))

                self.assertEqual(400, ex.exception.status_code)
                self.assertEqual("Current password does not match", ex.exception.detail)
