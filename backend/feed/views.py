from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FeedService
import logging

logger = logging.getLogger(__name__)


class FeedViewSet(viewsets.ViewSet):
    """
    API endpoints for feed functionality.

    Provides three feed types:
    - GET /api/feed/top-liked/ : UserFilledMadlibs sorted by like count
    - GET /api/feed/recent/ : UserFilledMadlibs sorted by created_at
    - GET /api/feed/discussed/ : UserFilledMadlibs sorted by comment count

    All endpoints support pagination and time filtering via query parameters.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feed_service = FeedService()

    def get_permissions(self):
        """
        All feed endpoints are public (AllowAny).
        """
        return [permissions.AllowAny()]

    def _validate_and_extract_params(self, request):
        """
        Validate and extract common query parameters.

        Args:
            request: HTTP request object

        Returns:
            Tuple of (limit, offset, time_filter) or Response object if validation fails
        """
        try:
            # Extract limit
            limit = request.query_params.get('limit', 50)
            try:
                limit = int(limit)
                if limit <= 0:
                    return Response(
                        {'error': 'limit must be a positive integer'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Cap at reasonable maximum
                limit = min(limit, 100)
            except ValueError:
                return Response(
                    {'error': 'limit must be a valid integer'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Extract offset
            offset = request.query_params.get('offset', 0)
            try:
                offset = int(offset)
                if offset < 0:
                    return Response(
                        {'error': 'offset must be a non-negative integer'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'error': 'offset must be a valid integer'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Extract and validate time_filter
            time_filter = request.query_params.get('time_filter', 'all')
            valid_filters = ['day', 'week', 'month', 'year', 'all']
            if time_filter not in valid_filters:
                return Response(
                    {'error': f'time_filter must be one of: {", ".join(valid_filters)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return limit, offset, time_filter

        except Exception as e:
            logger.error(f"Error validating parameters: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _build_paginated_response(self, results, limit, offset, time_filter, endpoint_name):
        """
        Build paginated response with next/previous URLs.

        Args:
            results: List of result items
            limit: Items per page
            offset: Current offset
            time_filter: Current time filter
            endpoint_name: Name of the endpoint for URL construction

        Returns:
            Response object with pagination metadata
        """
        # Build next/previous URLs
        next_url = None
        if len(results) == limit:  # May have more results
            next_url = f"?limit={limit}&offset={offset + limit}&time_filter={time_filter}"

        prev_url = None
        if offset > 0:
            prev_offset = max(0, offset - limit)
            prev_url = f"?limit={limit}&offset={prev_offset}&time_filter={time_filter}"

        return Response({
            'count': len(results),
            'next': next_url,
            'previous': prev_url,
            'results': results
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='top-liked')
    def top_liked(self, request):
        """
        Get UserFilledMadlibs sorted by like count (descending).

        Query Parameters:
        - limit (optional, default=50): Number of results per page
        - offset (optional, default=0): Skip N results for pagination
        - time_filter (optional, default='all'): One of 'day', 'week', 'month', 'year', 'all'

        GET /api/feed/top-liked/?limit=50&offset=0&time_filter=week

        Returns:
            Response with paginated madlibs sorted by likes_count (desc)
        """
        try:
            logger.debug("Getting top-liked feed")

            # Validate and extract parameters
            params = self._validate_and_extract_params(request)
            if isinstance(params, Response):
                return params
            limit, offset, time_filter = params

            # Get results from service
            results = self.feed_service.get_top_by_likes(
                limit=limit,
                offset=offset,
                time_filter=time_filter
            )

            logger.info(f"Retrieved {len(results)} top-liked madlibs (limit={limit}, offset={offset}, filter={time_filter})")

            return self._build_paginated_response(results, limit, offset, time_filter, 'top-liked')

        except Exception as e:
            logger.error(f"Error in top_liked endpoint: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='recent')
    def recent(self, request):
        """
        Get UserFilledMadlibs sorted by created_at (descending).

        Query Parameters:
        - limit (optional, default=50): Number of results per page
        - offset (optional, default=0): Skip N results for pagination
        - time_filter (optional, default='all'): One of 'day', 'week', 'month', 'year', 'all'

        GET /api/feed/recent/?limit=50&offset=0&time_filter=month

        Returns:
            Response with paginated madlibs sorted by created_at (desc)
        """
        try:
            logger.debug("Getting recent feed")

            # Validate and extract parameters
            params = self._validate_and_extract_params(request)
            if isinstance(params, Response):
                return params
            limit, offset, time_filter = params

            # Get results from service
            results = self.feed_service.get_most_recent(
                limit=limit,
                offset=offset,
                time_filter=time_filter
            )

            logger.info(f"Retrieved {len(results)} recent madlibs (limit={limit}, offset={offset}, filter={time_filter})")

            return self._build_paginated_response(results, limit, offset, time_filter, 'recent')

        except Exception as e:
            logger.error(f"Error in recent endpoint: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='discussed')
    def discussed(self, request):
        """
        Get UserFilledMadlibs sorted by comment count (descending).

        Query Parameters:
        - limit (optional, default=50): Number of results per page
        - offset (optional, default=0): Skip N results for pagination
        - time_filter (optional, default='all'): One of 'day', 'week', 'month', 'year', 'all'

        GET /api/feed/discussed/?limit=50&offset=0&time_filter=all

        Returns:
            Response with paginated madlibs sorted by comments_count (desc)
        """
        try:
            logger.debug("Getting most-discussed feed")

            # Validate and extract parameters
            params = self._validate_and_extract_params(request)
            if isinstance(params, Response):
                return params
            limit, offset, time_filter = params

            # Get results from service
            results = self.feed_service.get_most_discussed(
                limit=limit,
                offset=offset,
                time_filter=time_filter
            )

            logger.info(f"Retrieved {len(results)} most-discussed madlibs (limit={limit}, offset={offset}, filter={time_filter})")

            return self._build_paginated_response(results, limit, offset, time_filter, 'discussed')

        except Exception as e:
            logger.error(f"Error in discussed endpoint: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
