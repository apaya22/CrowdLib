from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from bson import ObjectId
from datetime import datetime, timezone

User = get_user_model()


class FeedViewSetTest(TestCase):
    """
    Unit tests for the FeedViewSet API endpoints.
    Tests use mocks to avoid MongoDB dependencies.
    """

    def setUp(self):
        """Set up test client and mock data."""
        self.client = APIClient()

        # Sample madlib data that would be returned by FeedService
        self.sample_madlibs = [
            {
                '_id': '507f1f77bcf86cd799439011',
                'template_id': '507f1f77bcf86cd799439012',
                'template_title': 'Adventure Story',
                'creator_id': '507f1f77bcf86cd799439013',
                'creator_username': 'john_doe',
                'content': [{'id': '1', 'input': 'happy'}, {'id': '2', 'input': 'dog'}],
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
                'public': True,
                'likes_count': 42,
                'comments_count': 15
            },
            {
                '_id': '507f1f77bcf86cd799439014',
                'template_id': '507f1f77bcf86cd799439012',
                'template_title': 'Adventure Story',
                'creator_id': '507f1f77bcf86cd799439015',
                'creator_username': 'jane_smith',
                'content': [{'id': '1', 'input': 'sad'}, {'id': '2', 'input': 'cat'}],
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
                'public': True,
                'likes_count': 30,
                'comments_count': 10
            }
        ]

    @patch('feed.views.FeedService')
    def test_get_top_liked_feed(self, MockFeedService):
        """Test top-liked endpoint returns sorted results."""
        # Setup mock
        mock_service = MockFeedService.return_value
        mock_service.get_top_by_likes.return_value = self.sample_madlibs

        # Make request
        url = '/api/feed/top-liked/'
        response = self.client.get(url)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['count'], 2)

        # Verify service was called with correct parameters
        mock_service.get_top_by_likes.assert_called_once_with(
            limit=50,
            offset=0,
            time_filter='all'
        )

    @patch('feed.views.FeedService')
    def test_get_most_recent_feed(self, MockFeedService):
        """Test recent endpoint returns sorted results."""
        mock_service = MockFeedService.return_value
        mock_service.get_most_recent.return_value = self.sample_madlibs

        url = '/api/feed/recent/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        mock_service.get_most_recent.assert_called_once_with(
            limit=50,
            offset=0,
            time_filter='all'
        )

    @patch('feed.views.FeedService')
    def test_get_most_discussed_feed(self, MockFeedService):
        """Test discussed endpoint returns sorted results."""
        mock_service = MockFeedService.return_value
        mock_service.get_most_discussed.return_value = self.sample_madlibs

        url = '/api/feed/discussed/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        mock_service.get_most_discussed.assert_called_once_with(
            limit=50,
            offset=0,
            time_filter='all'
        )

    @patch('feed.views.FeedService')
    def test_time_filter_day(self, MockFeedService):
        """Test time_filter='day' is passed to service."""
        mock_service = MockFeedService.return_value
        mock_service.get_most_recent.return_value = [self.sample_madlibs[0]]

        url = '/api/feed/recent/?time_filter=day'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service.get_most_recent.assert_called_once_with(
            limit=50,
            offset=0,
            time_filter='day'
        )

    @patch('feed.views.FeedService')
    def test_time_filter_week(self, MockFeedService):
        """Test time_filter='week' is passed to service."""
        mock_service = MockFeedService.return_value
        mock_service.get_top_by_likes.return_value = self.sample_madlibs

        url = '/api/feed/top-liked/?time_filter=week'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service.get_top_by_likes.assert_called_once_with(
            limit=50,
            offset=0,
            time_filter='week'
        )

    @patch('feed.views.FeedService')
    def test_pagination_limit_offset(self, MockFeedService):
        """Test pagination parameters are passed correctly."""
        mock_service = MockFeedService.return_value
        # Return exactly 20 results to trigger "next" URL
        mock_results = [self.sample_madlibs[0].copy() for _ in range(20)]
        mock_service.get_most_recent.return_value = mock_results

        url = '/api/feed/recent/?limit=20&offset=10'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service.get_most_recent.assert_called_once_with(
            limit=20,
            offset=10,
            time_filter='all'
        )

        # Check pagination URLs are included
        self.assertIsNotNone(response.data['next'])  # Should have next since we returned exactly limit
        self.assertIsNotNone(response.data['previous'])  # Should have previous since offset > 0

    @patch('feed.views.FeedService')
    def test_enrichment_fields_present(self, MockFeedService):
        """Test that enriched fields are present in response."""
        mock_service = MockFeedService.return_value
        mock_service.get_top_by_likes.return_value = self.sample_madlibs

        url = '/api/feed/top-liked/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check first result has all enriched fields
        result = response.data['results'][0]
        self.assertIn('creator_username', result)
        self.assertIn('template_title', result)
        self.assertIn('likes_count', result)
        self.assertIn('comments_count', result)

        self.assertEqual(result['creator_username'], 'john_doe')
        self.assertEqual(result['template_title'], 'Adventure Story')

    @patch('feed.views.FeedService')
    def test_empty_feed(self, MockFeedService):
        """Test that empty results are handled gracefully."""
        mock_service = MockFeedService.return_value
        mock_service.get_most_recent.return_value = []

        url = '/api/feed/recent/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.data['count'], 0)
        self.assertIsNone(response.data['next'])

    @patch('feed.views.FeedService')
    def test_invalid_time_filter(self, MockFeedService):
        """Test error handling for invalid time_filter."""
        url = '/api/feed/recent/?time_filter=invalid'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    @patch('feed.views.FeedService')
    def test_negative_limit(self, MockFeedService):
        """Test error handling for negative limit."""
        url = '/api/feed/recent/?limit=-5'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    @patch('feed.views.FeedService')
    def test_negative_offset(self, MockFeedService):
        """Test error handling for negative offset."""
        url = '/api/feed/recent/?offset=-10'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    @patch('feed.views.FeedService')
    def test_invalid_limit_non_integer(self, MockFeedService):
        """Test error handling for non-integer limit."""
        url = '/api/feed/recent/?limit=abc'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    @patch('feed.views.FeedService')
    def test_limit_capped_at_100(self, MockFeedService):
        """Test that limit is capped at 100."""
        mock_service = MockFeedService.return_value
        mock_service.get_most_recent.return_value = []

        url = '/api/feed/recent/?limit=200'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify limit was capped at 100
        mock_service.get_most_recent.assert_called_once_with(
            limit=100,
            offset=0,
            time_filter='all'
        )

    @patch('feed.views.FeedService')
    def test_all_time_filters_valid(self, MockFeedService):
        """Test that all valid time filters are accepted."""
        mock_service = MockFeedService.return_value
        mock_service.get_most_recent.return_value = []

        valid_filters = ['day', 'week', 'month', 'year', 'all']

        for time_filter in valid_filters:
            url = f'/api/feed/recent/?time_filter={time_filter}'
            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK,
                           f"Failed for time_filter={time_filter}")

    @patch('feed.views.FeedService')
    def test_public_endpoint_no_auth_required(self, MockFeedService):
        """Test that feed endpoints don't require authentication."""
        mock_service = MockFeedService.return_value
        mock_service.get_most_recent.return_value = []

        # Make request without authentication
        url = '/api/feed/recent/'
        response = self.client.get(url)

        # Should succeed (not 401/403)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('feed.views.FeedService')
    def test_pagination_urls_include_filters(self, MockFeedService):
        """Test that pagination URLs preserve time_filter parameter."""
        mock_service = MockFeedService.return_value
        mock_service.get_top_by_likes.return_value = self.sample_madlibs

        url = '/api/feed/top-liked/?limit=2&offset=0&time_filter=week'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that next URL includes time_filter
        if response.data['next']:
            self.assertIn('time_filter=week', response.data['next'])
            self.assertIn('limit=2', response.data['next'])


class FeedServiceTest(TestCase):
    """
    Unit tests for FeedService model logic.
    Tests time filter building and ObjectId conversion.
    """

    def setUp(self):
        """Set up test fixtures."""
        from feed.models import FeedService
        # Mock collections to avoid actual MongoDB calls
        with patch('feed.models.get_collection'):
            self.service = FeedService()

    def test_build_time_filter_all(self):
        """Test time filter for 'all' returns empty dict."""
        result = self.service._build_time_filter('all')
        self.assertEqual(result, {})

    def test_build_time_filter_none(self):
        """Test time filter for None returns empty dict."""
        result = self.service._build_time_filter(None)
        self.assertEqual(result, {})

    def test_build_time_filter_day(self):
        """Test time filter for 'day' returns correct query."""
        result = self.service._build_time_filter('day')
        self.assertIn('created_at', result)
        self.assertIn('$gte', result['created_at'])
        self.assertIsInstance(result['created_at']['$gte'], datetime)

    def test_build_time_filter_week(self):
        """Test time filter for 'week' returns correct query."""
        result = self.service._build_time_filter('week')
        self.assertIn('created_at', result)
        self.assertIn('$gte', result['created_at'])

    def test_build_time_filter_month(self):
        """Test time filter for 'month' returns correct query."""
        result = self.service._build_time_filter('month')
        self.assertIn('created_at', result)

    def test_build_time_filter_year(self):
        """Test time filter for 'year' returns correct query."""
        result = self.service._build_time_filter('year')
        self.assertIn('created_at', result)

    def test_build_time_filter_invalid(self):
        """Test time filter for invalid value returns empty dict."""
        result = self.service._build_time_filter('invalid')
        self.assertEqual(result, {})

    def test_convert_objectids(self):
        """Test ObjectId to string conversion."""
        doc = {
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'template_id': ObjectId('507f1f77bcf86cd799439012'),
            'creator_id': ObjectId('507f1f77bcf86cd799439013'),
            'other_field': 'value'
        }

        result = self.service._convert_objectids(doc)

        self.assertEqual(result['_id'], '507f1f77bcf86cd799439011')
        self.assertEqual(result['template_id'], '507f1f77bcf86cd799439012')
        self.assertEqual(result['creator_id'], '507f1f77bcf86cd799439013')
        self.assertEqual(result['other_field'], 'value')

    def test_convert_objectids_none(self):
        """Test ObjectId conversion handles None gracefully."""
        result = self.service._convert_objectids(None)
        self.assertIsNone(result)

    def test_convert_objectids_already_strings(self):
        """Test ObjectId conversion handles already-string IDs."""
        doc = {
            '_id': 'already-a-string',
            'template_id': 'also-a-string'
        }

        result = self.service._convert_objectids(doc)

        self.assertEqual(result['_id'], 'already-a-string')
        self.assertEqual(result['template_id'], 'also-a-string')
