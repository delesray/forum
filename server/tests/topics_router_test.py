from unittest import TestCase
from unittest.mock import Mock
from routers import topics as topics_router

mock_topics_services = Mock(spec='services.topics_services')
topics_router.topics_services = mock_topics_services
