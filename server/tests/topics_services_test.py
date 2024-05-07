from unittest import TestCase
from unittest.mock import Mock, patch
from data.models.topic import TopicResponse, TopicCreate
from data.models.user import User
from services import topics_services as topics
from mariadb import IntegrityError



TOPIC_ID = 1
TITLE = 'just a title'
USER_ID = 1
AUTHOR = 'just a man'
STATUS_OPEN = 0
BEST_REPLY_ID = None
CATEGORY_ID = 1
CATEGORY_NAME = 'Uncategorized'

# mock_db = Mock()
# topics.database = mock_db


def create_topic(topic_id):
    return TopicResponse(
        topic_id=topic_id,
        title=TITLE,
        user_id=USER_ID,
        author=AUTHOR,
        status='open',
        best_reply_id=BEST_REPLY_ID,
        category_id=CATEGORY_ID,
        category_name=CATEGORY_NAME)

    
# def fake_user():
#     return Mock(user_id=TEST_USER_ID, username=TEST_AUTHOR, password='password', email='email@mail.com')

class TopicsServices_Should(TestCase):
    
    # def setUp(self):
    #    mock_db.reset_mock()
   
    def test_getById_returnsTopicResponseObject_whenExists(self):
        with patch('services.topics_services.read_query') as mock_read_query:
            topic_id = 1
            mock_read_query.return_value = [
                (TOPIC_ID, TITLE, USER_ID, AUTHOR, STATUS_OPEN, BEST_REPLY_ID, CATEGORY_ID, CATEGORY_NAME)]

            expected = create_topic(topic_id)
            result = topics.get_by_id(topic_id)

            self.assertEqual(expected, result)
    
    
    def test_getById_returnsNone_whenNoSuchTopic(self):
        with patch('services.topics_services.read_query') as mock_read_query:
            topic_id = 1
            mock_read_query.return_value = []

            expected = None
            result = topics.get_by_id(topic_id)

            self.assertEqual(expected, result)
          
        
    def test_exists_returns_True_when_topicIsPresent(self):
        with patch('services.topics_services.read_query') as mock_read_query:
            mock_read_query.return_value = [(1)]
        
            result = topics.exists(TOPIC_ID)
        
            self.assertTrue(result)
               
               
    def test_exists_returns_False_when_noTopic(self):
        with patch('services.topics_services.read_query') as mock_read_query:
            mock_read_query.return_value = []
        
            result = topics.exists(TOPIC_ID)
        
            self.assertFalse(result)
        
        
    def test_getTotalCount_returns_countOfTopics_when_SqlAndParams_areProvided(self):
        with patch('services.topics_services.query_count') as mock_query_count:
           mock_query_count.return_value = 10
           sql = 'SELECT * FROM table'
           params = ('filter_1', 'filter_2')
           
           expected = 10
           result = topics.get_total_count(sql, params) 
        
           self.assertEqual(expected, result)
           mock_query_count.assert_called_once_with(
                'SELECT COUNT(*) FROM (SELECT * FROM table) as filtered_topics',
                ('filter_1', 'filter_2')
            ) 
    
    def test_getAll_returns_ListOfTopicsAndTotalCount_when_noFilters(self):
        pass
    
    def test_getAll_returns_ListOfTopicsAndTotalCount_when_isSearch(self):
        pass
    
    def test_getAll_returns_ListOfTopicsAndTotalCount_when_filteredByUsername(self):
        pass
    
    def test_getAll_returns_ListOfTopicsAndTotalCount_when_filteredByStatus(self):
        pass
    
    def test_getAll_returns_ListOfTopicsAndTotalCount_when_filteredByCategory(self):
         pass
    
    def test_getAll_returns_ListOfTopicsAndTotalCount_when_isSort(self):
        pass
        
      
    def test_create_returnsTopicId(self):
        with patch('services.topics_services.insert_query') as mock_insert_query:
            topic_id = 1
            mock_insert_query.return_value = topic_id

            expected = 1
            result = topics.create(topic=TopicCreate(title=TITLE, category_id=CATEGORY_ID), user_id=USER_ID)

            self.assertEqual(expected, result)

    #there are no unique constraints for topics in the db except for the primary key constraint
    # def test_create_raise_IntegrityError(self):
    #     with patch('services.topics_services.insert_query') as mock_insert_query:
    #         mock_insert_query.side_effect = IntegrityError("Integrity constraint violated")
    
    #         with self.assertRaises(IntegrityError):
    #              topics.create(topic=TopicCreate(title=TITLE, category_id=CATEGORY_ID), user_id=USER_ID)   

    
    def test_updateBestReply_updatesBestReplyId_returns_Message(self):
        with patch('services.topics_services.update_query') as mock_update_query:
            best_reply_id = 1
        
            expected = f"Project Best Reply Id updated to {best_reply_id}"
            result = topics.update_best_reply(TOPIC_ID, best_reply_id)
            
            self.assertEqual(expected, result)
            
    
        
        