from unittest import TestCase
from unittest.mock import patch
from data.models.topic import TopicResponse, TopicCreate
from data.models.user import User
from services import topics_services as topics
from mariadb import IntegrityError


#TOPIC
TOPIC_ID = 1
TITLE = 'just a title'
USER_ID = 1
AUTHOR = 'just a man'
STATUS_OPEN = 0
BEST_REPLY_ID = None
CATEGORY_ID = 1
CATEGORY_NAME = 'Uncategorized'

# pagination params
PAGE = 1
SIZE = 1


def create_topic(topic_id, topic_title=TITLE, author=AUTHOR):
    return TopicResponse(
        topic_id=topic_id,
        title=topic_title,
        user_id=USER_ID,
        author=author,
        status='open',
        best_reply_id=BEST_REPLY_ID,
        category_id=CATEGORY_ID,
        category_name=CATEGORY_NAME)

  
class TopicsServices_Should(TestCase):
   
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
    
    def test_getAll_returns_ListOfTopicResponseObjectssAndTotalCount_when_TopicsExist_when_noFilters(self):
        with patch('services.topics_services.read_query') as mock_read_query, \
                patch('services.topics_services.get_total_count') as mock_get_total_count:
                    
            topic_id_1, topic_id_2, topic_id_3 = 1, 2, 3
            mock_read_query.return_value = [(topic_id_1, TITLE, USER_ID, AUTHOR, STATUS_OPEN, BEST_REPLY_ID, CATEGORY_ID, CATEGORY_NAME),
                                            (topic_id_2, TITLE, USER_ID, AUTHOR, STATUS_OPEN, BEST_REPLY_ID, CATEGORY_ID, CATEGORY_NAME),
                                            (topic_id_3, TITLE, USER_ID, AUTHOR, STATUS_OPEN, BEST_REPLY_ID, CATEGORY_ID, CATEGORY_NAME)]
            
            mock_get_total_count.return_value = 3

            expected_topics = [create_topic(topic_id_1),
                               create_topic(topic_id_2),
                               create_topic(topic_id_3)]
            expected_total_count = 3
            expected_result = (expected_topics, expected_total_count)
            result = topics.get_all(page=PAGE, size=SIZE)

            self.assertEqual(expected_result, result)
            
    def test_getAll_returnsEmptyTuple_whenNoTopics(self): 
        with patch('services.topics_services.read_query') as mock_read_query, \
                patch('services.topics_services.get_total_count') as mock_get_total_count: 
                    
            mock_read_query.return_value = []  
            mock_get_total_count.return_value = 0
            expected_result = ([], 0)  
            
            result = topics.get_all(page=PAGE, size=SIZE)

            self.assertEqual(expected_result, result) 
    
    def test_getAll_checksIf_ReadQueryCalled_withCorrectSqlAndParams_whenSearchFilter(self):
        with patch('services.topics_services.read_query') as mock_read_query, \
                patch('services.topics_services.get_total_count') as mock_get_total_count:
                    
            mock_get_total_count.return_value = 1
                   
            expected_sql= (
    'SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id, t.category_id, c.name ' 
    'FROM topics t ' 
    'JOIN users u ON t.user_id = u.user_id ' 
    'JOIN categories c ON t.category_id = c.category_id ' 
    'WHERE t.title LIKE ? ' 
    'LIMIT ? OFFSET ?'
)
            search_filter = 'example'
            limit = SIZE
            offset = SIZE * (PAGE - 1)  
            expected_params = (f'%{search_filter}%', limit, offset) 
            
            topics.get_all(PAGE, SIZE, search=search_filter)                                    
            mock_read_query.assert_called_with(expected_sql, expected_params)
            
    
    def test_getAll_checksIf_ReadQueryCalled_withCorrectSqlAndParams_whenAllFiltersAndSortApplied(self):
        with patch('services.topics_services.read_query') as mock_read_query, \
                patch('services.topics_services.get_total_count') as mock_get_total_count:
                    
            mock_get_total_count.return_value = 1
                   
            expected_sql = (
    'SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id, t.category_id, c.name '
    'FROM topics t '
    'JOIN users u ON t.user_id = u.user_id '
    'JOIN categories c ON t.category_id = c.category_id '
    'WHERE t.title LIKE ? '
    'AND u.username = ? '
    'AND c.name = ? '
    'AND t.is_locked = ? '
    'ORDER BY title IS NULL, title ASC '
    'LIMIT ? OFFSET ?'
)
                          
            search_filter = 'example'
            username_filter = AUTHOR
            category_filter = CATEGORY_NAME
            status_filter = 0
            sort = 'asc'
            sort_by = 'title'
            limit = SIZE
            offset = SIZE * (PAGE - 1)  
            expected_params = (f'%{search_filter}%', username_filter, category_filter, status_filter, limit, offset) 
            
            topics.get_all(PAGE,
                           SIZE, 
                           search=search_filter, 
                           username=username_filter,
                           category=category_filter,
                           status='open',
                           sort=sort,
                           sort_by=sort_by
                       ) 
                                               
            mock_read_query.assert_called_with(expected_sql, expected_params)
            
              
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
        
            expected = f"Best Reply Id updated to {best_reply_id}"
            result = topics.update_best_reply(TOPIC_ID, best_reply_id)
            
            self.assertEqual(expected, result)
            
    
    def test_get_topic_replies_returnsListWithReplies_whenExist(self):
        pass  
    
    def test_get_topic_replies_returnsEmptyList_whenNoReplies(self):
        pass    
          
    def test_validate_topic_access_returnsErrorResponse_whenTopicNotExist(self):
        pass
    
    def test_validate_topic_access_returnsErrorResponse_whenTopicIsLocked(self):
        pass
    
    def test_validate_topic_access_returnsErrorResponse_whenUserIsNotOwner(self):
        pass
    
    def test_validate_topic_access_returnsNone_whenValidatingSuccessful(self):
        pass