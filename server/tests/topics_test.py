from unittest import TestCase
from unittest.mock import Mock, patch
from routers import topics as topics_router
from routers.replies import HTTPException
from data.models.category import Category
from data.models.topic import TopicResponse, TopicsPaginate
from common.utils import PaginationInfo, Links
from common.responses import SC
#from fastapi.testclient import TestClient


#client = TestClient(topics_router)

PAGE = 1
SIZE = 1

class TestCategory:
    ID = 1
    NAME = 'test_name'
    LOCKED = False
    PRIVATE = False
    VALUES_TUPLE = (ID, NAME, LOCKED, PRIVATE)
    OBJ = Category.from_query(*VALUES_TUPLE)
    
class TestTopic:
    ID = 1
    TITLE = 'test_title'
    USER_ID = 1
    AUTHOR = 'test_author'
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
    

class TopicssRouter_Should(TestCase):
    def test_getAllTopics_returnsTopicPaginateObject_when_TopicsExist(self):
        with patch('services.users_services.exists_by_username') as mock_exists_by_username, \
          patch('services.categories_services.exists_by_name') as mock_exists_by_name, \
          patch('services.topics_services.get_all') as mock_get_all:
            
            fake_topics_total = 1   
            pagination_info = create_pagination_info(fake_topics_total)
                        
            mock_exists_by_username.return_value = True
            mock_exists_by_name.return_value = True
            mock_get_all.return_value = ([TestTopic.OBJ], pagination_info, FAKE_LINKS)
                         
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
          patch('services.topics_services.get_all') as mock_get_all:
                
            fake_topics_total = 0
            pagination_info = create_pagination_info(fake_topics_total)
            mock_exists_by_username.return_value = True
            mock_exists_by_name.return_value = True
            mock_get_all.return_value = ([], pagination_info, FAKE_LINKS )
            
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
            
                
    def test_getAllTopics_raises404_whenCategoryNotExists(self):
        with patch('services.categories_services.exists_by_name') as mock_exists_by_name:
            mock_exists_by_name.return_value = False

            with self.assertRaises(HTTPException) as ex:
                topics_router.get_all_topics(Mock(), page=PAGE, size=SIZE, category='fake_category')
                
            self.assertEqual(404, ex.exception.status_code)
            self.assertEqual('Category not found', ex.exception.detail)
                
                
    def test_getAllTopics_raises400_whenInvalidStatusParameterProvided(self):
        
        with self.assertRaises(HTTPException) as ex:
                topics_router.get_all_topics(Mock(), page=PAGE, size=SIZE, status='invalid status')

                self.assertEqual(400, ex.exception.status_code)
                self.assertEqual('Invalid status value', ex.exception.detail)
                
                
    def test_getAllTopics_raises400_whenInvalidSortParameterProvided(self):
        
        with self.assertRaises(HTTPException) as ex:
                topics_router.get_all_topics(Mock(), page=PAGE, size=SIZE, sort='invalid sort')

                self.assertEqual(400, ex.exception.status_code)
                self.assertEqual('Invalid sort parameter', ex.exception.detail)
                
                
    def test_getAllTopics_raises400_whenInvalidSort_byParameterProvided(self):
        
        with self.assertRaises(HTTPException) as ex:
                topics_router.get_all_topics(Mock(), page=PAGE, size=SIZE, sort_by='invalid sort_by')

                self.assertEqual(400, ex.exception.status_code)
                self.assertEqual('Invalid sort_by parameter', ex.exception.detail)
        