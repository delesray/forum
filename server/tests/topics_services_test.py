from unittest import TestCase
from unittest.mock import Mock
from data.models.topic import TopicResponse, TopicCreate
from data.models.user import User
from services import topics_services
from mariadb import IntegrityError


TEST_TOPIC_ID = 1
TEST_TITLE = 'just a title'
TEST_USER_ID = 1
TEST_AUTHOR = 'just a man'
TEST_STATUS = 0
TEST_BEST_REPLY = None
TEST_CATEGORY_ID = 1
TEST_CATEGORY_NAME = 'Uncategorized'

mock_db = Mock()
topics_services.database = mock_db


def create_topic(topic_id):
    return TopicResponse(
        topic_id=topic_id,
        title=TEST_TITLE,
        user_id=TEST_USER_ID,
        author=TEST_AUTHOR,
        status=TEST_STATUS,
        best_reply_id=TEST_BEST_REPLY,
        category_id=TEST_CATEGORY_ID,
        category_name=TEST_CATEGORY_NAME)

def fake_TopicCreate():
    return Mock(title=TEST_TITLE, category_id=TEST_CATEGORY_ID)
    
def fake_user():
    return Mock(user_id=TEST_USER_ID, username=TEST_AUTHOR, password='password', email='email@mail.com')

class TopicsServices_Should(TestCase):
    
    def setUp(self):
       mock_db.reset_mock()
    
    def test_getById_returns_singleTopic(self):
        mock_db.read_query.return_value = [(TEST_TOPIC_ID, TEST_TITLE, TEST_USER_ID, TEST_AUTHOR, 
                                            TEST_STATUS, TEST_BEST_REPLY, TEST_CATEGORY_ID, TEST_CATEGORY_NAME)]
        expected = create_topic(TEST_TOPIC_ID)

        result = topics_services.get_by_id(TEST_TOPIC_ID)

        self.assertEqual(expected, result)
        
        
    def test_getById_returns_None(self):
        mock_db.read_query.return_value = []
        
        result = topics_services.get_by_id(TEST_TOPIC_ID)
    
        self.assertIsNone(result)
        
        
    def test_exists_returns_True_when_topicIsPresent(self):
        mock_db.read_query.return_value = [(1)]
        
        result = topics_services.exists(TEST_TOPIC_ID)
        
        self.assertTrue(result)
               
               
    def test_exists_returns_False_when_noTopic(self):
        mock_db.read_query.return_value = []
        
        result = topics_services.exists(TEST_TOPIC_ID)
        
        self.assertFalse(result)
        
    def test_getTotalCount_returns_countOfTopics_when_SqlAndParams_areProvided(self):
        mock_db.query_count.return_value = 10
        sql = 'SQL QUERY TO BE EXECUTED'
        params = ('filter_1', 'filter_2')
        expected = 10
        
        result = topics_services.get_total_count(sql, params) 
        
        self.assertEqual(expected, result) 
    
    def test_getAll_returns_ListOfTopicsAndTotalCount_when_noFilters(self):
        pass
    
    def test_getAll_returns_ListOfTopicsAndTotalCount_when_isSearch(self):
        pass
    
    def test_getAll_returns_ListOfTopicsAndTotalCount_when_filteredByUsername(self):
        pass
    
    def test_getAll_returns_ListOfTopicsAndTotalCount_when_filteredByStatus(self):
        pass
    
    # def test_getAll_returns_ListOfTopicsAndTotalCount_when_filteredByCategory(self):
    #     pass
    
    def test_getAll_returns_ListOfTopicsAndTotalCount_when_isSort(self):
        pass
        
    def test_create_createsTopic_returns_GeneratedId(self):
        generated_id = TEST_TOPIC_ID
        mock_db.read_query.return_value = [(generated_id)]
        expected = generated_id
        
        result = topics_services.create(fake_TopicCreate(), fake_user())
        
        self.assertEqual(expected, result)  
    
    
    def test_create_raise_IntegrityError(self):
        mock_db.insert_query.side_effect = IntegrityError
        
        with self.assertRaises(IntegrityError):
            topics_services.create(fake_TopicCreate(), fake_user())


    def test_updateBestReply_updatesBestReplyId_returns_Message(self):
        best_reply_id = 1
        mock_db.update_query.return_value = True
        expected = f"Project Best Reply Id updated to {best_reply_id}"
        
        result = topics_services.update_best_reply(TEST_TOPIC_ID, best_reply_id)
        
        self.assertEqual(expected, result)  
    
        
        