from unittest import TestCase
from unittest.mock import Mock, patch
from routers import topics as topics_router
from routers.replies import HTTPException
from data.models.category import Category
from data.models.topic import TopicResponse, TopicsPaginate, TopicRepliesPaginate
from data.models.reply import ReplyResponse
from common.utils import PaginationInfo, Links
from common.responses import SC
from services.replies_services import get_all


PAGE = 1
SIZE = 1

class TestCategory:
    ID = 1
    NAME = 'TestName'
    LOCKED = False
    PRIVATE = False
    VALUES_TUPLE = (ID, NAME, LOCKED, PRIVATE)
    OBJ = Category.from_query(*VALUES_TUPLE)
    
class TestTopic:
    ID = 1
    TITLE = 'TestTitle'
    USER_ID = 1
    AUTHOR = 'TestAuthor'
    STATUS = 0
    BEST_REPLY_ID = None 
    CATEGORY_ID = 1
    CATEGORY_NAME = 'Uncategorized'
    PRIVATE = False
    VALUES_TUPLE = (ID, TITLE, USER_ID, AUTHOR, STATUS, BEST_REPLY_ID, CATEGORY_ID, CATEGORY_NAME)
    OBJ = TopicResponse.from_query(*VALUES_TUPLE)
    
FAKE_LINKS = Links(
               self="URL of the current page",
               first="URL of the first page",
               last="URL of the last page",
               next='URL of the next page, if it exists',
               prev="URL of the previous page, if it exists"
            )

def create_pagination_info(total_elements): 
    return PaginationInfo(
        total_elements=total_elements,
        page=PAGE,
        size=SIZE,
        pages=total_elements
    )
    
test_reply=ReplyResponse(
        reply_id=1,
        text='text',
        username='username',
        topic_id=1)

def fake_user():
    user = Mock()
    user.is_admin = False

    return user

def fake_category(is_private: bool = False , is_locked: bool = False):
    category = Mock()
    category.category_id = 1
    category.is_private = is_private
    category.is_locked = is_locked

    return category
    
class TopicsRouter_Should(TestCase):
      
    def test_getAllTopics_returnsTopicPaginateObject_when_TopicsExist(self):
        with patch('services.users_services.exists_by_username') as mock_exists_by_username, \
          patch('services.categories_services.exists_by_name') as mock_exists_by_name, \
          patch('services.topics_services.get_topics_paginate_links') as mock_topics_paginate_links:
            
            fake_topics_total = 1   
            pagination_info = create_pagination_info(fake_topics_total)
                        
            mock_exists_by_username.return_value = True
            mock_exists_by_name.return_value = True
            mock_topics_paginate_links.return_value = ([TestTopic.OBJ], pagination_info, FAKE_LINKS)
                         
            expected_result = TopicsPaginate(
                           topics=[TestTopic.OBJ],
                           pagination_info=pagination_info,
                           links=FAKE_LINKS
                           )
            result = topics_router.get_all_topics(Mock(), page=PAGE, size=SIZE)
            
            self.assertEqual(expected_result, result)
            
            
    def test_getAllTopics_returnsEmptyList_when_NoTopics(self):
        with patch('services.users_services.exists_by_username') as mock_exists_by_username, \
          patch('services.categories_services.exists_by_name') as mock_exists_by_name, \
          patch('services.topics_services.get_topics_paginate_links') as mock_topics_paginate_links:
                
            fake_topics_total = 0
            pagination_info = create_pagination_info(fake_topics_total)
            mock_exists_by_username.return_value = True
            mock_exists_by_name.return_value = True
            mock_topics_paginate_links.return_value = ([], pagination_info, FAKE_LINKS )
            
            expected_result = []
            result = topics_router.get_all_topics(Mock(), page=PAGE, size=SIZE)
            
            self.assertEqual(expected_result, result)
            
            
    def test_getAllTopics_raisesHTTPException_whenUsernameNotExists(self):
        with patch('services.users_services.exists_by_username') as mock_exists_by_username:
              
            mock_exists_by_username.return_value = False 
    
            with self.assertRaises(HTTPException) as ex:
                topics_router.get_all_topics(Mock(), page=PAGE, size=SIZE, username='fake_username')

                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('User not found', ex.exception.detail)
            
                
    def test_getAllTopics_raisesHTTPException_whenCategoryNotExists(self):
        with patch('services.categories_services.exists_by_name') as mock_exists_by_name:
            mock_exists_by_name.return_value = False

            with self.assertRaises(HTTPException) as ex:
                topics_router.get_all_topics(Mock(), page=PAGE, size=SIZE, category='fake_category')
                
            self.assertEqual(404, ex.exception.status_code)
            self.assertEqual('Category not found', ex.exception.detail)
                
                
    def test_getAllTopics_raisesHTTPException_whenInvalidStatusParameterProvided(self):
        
        with self.assertRaises(HTTPException) as ex:
                topics_router.get_all_topics(Mock(), page=PAGE, size=SIZE, status='invalid status')

                self.assertEqual(400, ex.exception.status_code)
                self.assertEqual('Invalid status value', ex.exception.detail)
                
                
    def test_getAllTopics_raisesHTTPException_whenInvalidSortParameterProvided(self):
        
        with self.assertRaises(HTTPException) as ex:
                topics_router.get_all_topics(Mock(), page=PAGE, size=SIZE, sort='invalid sort')

                self.assertEqual(400, ex.exception.status_code)
                self.assertEqual('Invalid sort parameter', ex.exception.detail)
                
                
    def test_getAllTopics_raisesHTTPException_whenInvalidSort_byParameterProvided(self):
        
        with self.assertRaises(HTTPException) as ex:
                topics_router.get_all_topics(Mock(), page=PAGE, size=SIZE, sort_by='invalid sort_by')

                self.assertEqual(400, ex.exception.status_code)
                self.assertEqual('Invalid sort_by parameter', ex.exception.detail)
                
                
    def test_getTopicById_returnsTopicRepliesPaginateObject_when_TopicsExist_userHasAccessToTopic(self):
        with patch('services.topics_services.get_by_id') as mock_topic_by_id, \
          patch('services.categories_services.get_by_id') as mock_category_by_id, \
          patch('services.categories_services.has_access_to_private_category') as mock_access, \
          patch('services.replies_services.get_all') as mock_get_all_replies:
              
            pagination_info = create_pagination_info(1)            
            mock_topic_by_id.return_value = TestTopic.OBJ
            mock_category_by_id.return_value = TestCategory.OBJ
            mock_access.return_value = True
            mock_get_all_replies.return_value = ([test_reply], pagination_info, FAKE_LINKS)
                         
            expected_result = TopicRepliesPaginate(
                           topic=TestTopic.OBJ,
                           replies=[test_reply],
                           pagination_info=pagination_info,
                           links=FAKE_LINKS
                           )
            result = topics_router.get_topic_by_id(TestTopic.ID, Mock(), Mock(), page=PAGE, size=SIZE)
            
            self.assertEqual(expected_result, result)
        
        
    def test_getTopicById_raisesHTTPException_whenTopicNotExists(self):
        with patch('services.topics_services.get_by_id') as mock_topic_by_id:
              
            mock_topic_by_id.return_value = None 
    
            with self.assertRaises(HTTPException) as ex:
                topics_router.get_topic_by_id(TestTopic.ID, Mock(), Mock(), page=PAGE, size=SIZE)

                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('Topic #ID:1 does not exist', ex.exception.detail)
                
                
    def test_getTopicById_raisesHTTPException_whenCategoryPrivate_userNoPermission(self):
        with patch('services.categories_services.get_by_id') as mock_category_by_id:
            
            mock_category_by_id.return_value = fake_category(is_private=True)
            anonymous_user = topics_router.AnonymousUser()
 
            with self.assertRaises(HTTPException) as ex:
                topics_router.get_topic_by_id(TestTopic.ID, anonymous_user, Mock(), page=PAGE, size=SIZE)

                self.assertEqual(401, ex.exception.status_code)
                self.assertEqual('Login to view topics in private categories', ex.exception.detail)
                
                
    def test_getTopicById_raisesHTTPException_whenUserHasNotAccessToTopic(self):
        with patch('services.topics_services.get_by_id') as mock_topic_by_id, \
          patch('services.categories_services.get_by_id') as mock_category_by_id, \
          patch('services.categories_services.has_access_to_private_category') as mock_access:
            
            mock_topic_by_id.return_value = TestTopic.OBJ  
            mock_category_by_id.return_value = fake_category(is_private=True)
            mock_access.return_value = False
        
            with self.assertRaises(HTTPException) as ex:
                topics_router.get_topic_by_id(TestTopic.ID, fake_user(), Mock(), page=PAGE, size=SIZE)

                self.assertEqual(403, ex.exception.status_code)
                self.assertEqual('You do not have permission to access this private category', ex.exception.detail)
                
                
    def test_createTopic_returnsCorrectMsg_whenCategoryExistsAndNotLockedNotPrivate_userHasAccessToCategory(self):
        with patch('services.categories_services.get_by_id') as mock_category_by_id, \
          patch('services.topics_services.create') as mock_create:
                
            mock_category_by_id.return_value = fake_category()
            mock_create.return_value = TestTopic.ID
            new_topic= topics_router.TopicCreate(title='TestTitle', category_id=TestCategory.ID)
            
            expected = f'Topic 1 was successfully created!'
            result = topics_router.create_topic(new_topic, fake_user())

            self.assertEqual(expected, result)
            
            
    def test_createTopic_raisesHTTPException_whenCategoryNotExists(self):
        with patch('services.categories_services.get_by_id') as mock_category_by_id:
              
            mock_category_by_id.return_value = None 
            new_topic= topics_router.TopicCreate(title='TestTitle', category_id=TestCategory.ID)
    
            with self.assertRaises(HTTPException) as ex:
                topics_router.create_topic(new_topic, fake_user())

                self.assertEqual(404, ex.exception.status_code)
                self.assertEqual('Category #ID:1 does not exist', ex.exception.detail)
              
              
    def test_createTopic_raisesHTTPException_whenCategoryIsLocked(self):
        with patch('services.categories_services.get_by_id') as mock_category_by_id:
            
            category = TestCategory.OBJ
            category.is_locked = True  
            mock_category_by_id.return_value = category
            new_topic= topics_router.TopicCreate(title='TestTitle', category_id=TestCategory.ID)
    
            with self.assertRaises(HTTPException) as ex:
                topics_router.create_topic(new_topic, fake_user())

                self.assertEqual(403, ex.exception.status_code)
                self.assertEqual('Category #ID:1, Name: TestName is locked', ex.exception.detail)
                
    def test_createTopic_raisesHTTPException_whenCategoryPrivate_userNoPermission(self):
        with patch('services.categories_services.get_by_id') as mock_category_by_id, \
          patch('services.categories_services.has_write_access') as mock_write_access:
            
            category = TestCategory.OBJ
            category.is_private = True  
            mock_category_by_id.return_value = category
            mock_write_access.return_value = False
            new_topic= topics_router.TopicCreate(title='TestTitle', category_id=TestCategory.ID)

            with self.assertRaises(HTTPException) as ex:
                topics_router.create_topic(new_topic, fake_user())

                self.assertEqual(403, ex.exception.status_code)
                self.assertEqual('You do not have permission to post in this private category', ex.exception.detail)
              
                
                
                
                
            
            
            