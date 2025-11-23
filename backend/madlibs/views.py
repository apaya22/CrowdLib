from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import MadLibTemplate, UserFilledMadlibs
import logging

from bson.errors import InvalidId

logger = logging.getLogger(__name__)



class MadLibTemplateViewSet(viewsets.ViewSet):
    """
    API endpoints for managing madlib templates.

    - POST /api/templates/ : Create a new template
    - GET /api/templates/ : List all templates
    - GET /api/templates/{id}/ : Retrieve a template by ID
    - PUT /api/templates/{id}/ : Update a template
    - DELETE /api/templates/{id}/ : Delete a template
    - GET /api/templates/search/ : Search templates by title
    """
    def get_permissions(self):
        """
        permission dictionary. Automatically called by rest_framework.permssions
        """
        permission_classes = {
            'list': [permissions.AllowAny],
            'create': [permissions.IsAdminUser],
            'retrieve': [permissions.AllowAny],
            'update': [permissions.IsAdminUser],
            'destroy': [permissions.IsAdminUser],
            'search' : [permissions.AllowAny],
            'admin_stats': [permissions.IsAdminUser],
        }

        return [
            permission()
            for permission in permission_classes.get(self.action, [permissions.IsAdminUser])
        ]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_service = MadLibTemplate()

    def list(self, request):
        """
        List all madlib templates with optional limit.

        Query Parameters:
        - limit: Maximum number of templates to retrieve (default: 100)

        GET /api/templates/?limit=50
        """
        try:
            logger.debug("Listing madlib templates")
            limit = request.query_params.get('limit', 100)

            # Validate limit is a positive integer
            try:
                limit = int(limit)
                if limit <= 0:
                    limit = 100
            except ValueError:
                limit = 100

            templates = self.template_service.get_all(limit=limit)
            logger.info(f"Listed {len(templates)} madlib templates")

            return Response(
                {'count': len(templates), 'results': templates},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error listing madlib templates: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request):
        """
        Create a new madlib template.

        Expected JSON:
        {
            "title": "Adventure Story",
            "description": "Fill in the blanks to create your own adventure!",
            "blanks": [
                {
                    "id": "1",
                    "placeholder": "Enter an adjective",
                    "type": "adjective"
                },
                {
                    "id": "2",
                    "placeholder": "Enter a noun",
                    "type": "noun"
                }
            ],
            "story": "Once upon a time, there was a [1] [2]..."
        }
        """
        try:
            data = request.data
            logger.debug(f"Creating madlib template: {data.get('title', 'N/A')}")

            # Validate required fields
            required_fields = ['title', 'story']
            if not all(field in data for field in required_fields):
                logger.warning(f"Missing required fields in create request")
                return Response(
                    {'error': f'Missing required fields: {required_fields}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Ensure title is not empty
            if not data['title'].strip():
                logger.warning("Title is empty in create request")
                return Response(
                    {'error': 'Title cannot be empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            template_id = self.template_service.create(data)

            if not template_id:
                logger.error("Failed to create madlib template")
                return Response(
                    {'error': 'Failed to create template'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            logger.info(f"Madlib template created: {template_id}")
            return Response(
                {'id': template_id, 'message': 'Template created successfully'},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Error creating madlib template: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """
        Retrieve a madlib template by ID.

        GET /api/templates/{id}/
        """
        if not pk:
            logger.warning("Retrieve template called without ID")
            return Response(
                {'error': 'Missing madlib ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            logger.debug(f"Retrieving madlib template: {pk}")
            template = self.template_service.get_by_id(str(pk))

            if not template:
                logger.info(f"Madlib template not found: {pk}")
                return Response(
                    {'error': 'Template not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            logger.info(f"Madlib template retrieved: {pk}")
            return Response(template, status=status.HTTP_200_OK)

        except InvalidId:
            logger.warning(f"Invalid madlib template ID format: {pk}")
            return Response(
                {'error': 'Invalid template ID format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error retrieving madlib template {pk}: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        """
        Update a madlib template.

        Expected JSON (all fields optional):
        {
            "title": "Updated Title",
            "description": "Updated description",
            "story": "Updated story with [1] and [2]",
            "blanks": [...]
        }
        """
        try:
            data = request.data
            logger.debug(f"Updating madlib template: {pk}")

            if not data or pk:
                logger.warning("Update template called without data or ID")
                return Response(
                    {'error': 'No data provided for update'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            success = self.template_service.update(str(pk), data)

            if not success:
                logger.info(f"Template not found or update failed: {pk}")
                return Response(
                    {'error': 'Template not found or update failed'},
                    status=status.HTTP_404_NOT_FOUND
                )

            logger.info(f"Madlib template updated: {pk}")
            return Response(
                {'message': 'Template updated successfully'},
                status=status.HTTP_200_OK
            )

        except InvalidId:
            logger.warning(f"Invalid madlib template ID format: {pk}")
            return Response(
                {'error': 'Invalid template ID format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating madlib template {pk}: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """
        Delete a madlib template.

        DELETE /api/templates/{id}/
        """
        if not pk:
            logger.warning("Destroy template called without ID")
            return Response(
                {'error': 'No data provided for update'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            logger.debug(f"Deleting madlib template: {pk}")
            success = self.template_service.delete(str(pk))

            if not success:
                logger.info(f"Madlib template not found: {pk}")
                return Response(
                    {'error': 'Template not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            logger.info(f"Madlib template deleted: {pk}")
            return Response(
                {'message': 'Template deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )

        except InvalidId:
            logger.warning(f"Invalid madlib template ID format: {pk}")
            return Response(
                {'error': 'Invalid template ID format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error deleting madlib template {pk}: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for templates by title.

        Query Parameters:
        - title: Title to search for (required)
        - exact: Whether to search for exact match (default: false)

        GET /api/templates/search/?title=Adventure
        GET /api/templates/search/?title=Adventure&exact=true
        """
        try:
            title = request.query_params.get('title', '').strip()

            if not title:
                logger.warning("Search templates called without title parameter")
                return Response(
                    {'error': 'title query parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            exact = request.query_params.get('exact', 'false').lower() == 'true'
            logger.debug(f"Searching madlib templates: title='{title}', exact={exact}")

            templates = self.template_service.search_by_title(title, exact=exact)
            logger.info(f"Search found {len(templates)} madlib templates matching '{title}'")

            return Response(
                {
                    'query': title,
                    'exact': exact,
                    'count': len(templates),
                    'results': templates
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error searching madlib templates: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class UserFilledMadlibsViewSet(viewsets.ViewSet):
    """
    API endpoints for managing user-filled madlibs.

    - POST /api/madlibs/create/ : Create a new filled madlib
    - GET /api/madlibs/{id}/ : Retrieve a filled madlib by ID
    - GET /api/madlibs/creator/{creator_id}/ : Get all madlibs by creator
    - PUT /api/madlibs/{id}/ : Update a filled madlib
    - DELETE /api/madlibs/{id}/ : Delete a filled madlib
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.madlibs_service = UserFilledMadlibs()
        
    def get_permissions(self):
        """
        permission dictionary. Automatically called by rest_framework.permssions
        """
        permission_classes = {
            'list': [permissions.AllowAny],
            'create': [permissions.IsAuthenticated],
            'retrieve': [permissions.AllowAny],
            'update': [permissions.IsAuthenticated],
            'destroy': [permissions.IsAuthenticated],
            'profile': [permissions.IsAuthenticated],
            'by_creator': [permissions.AllowAny],
            'admin_stats': [permissions.IsAdminUser],
        }

        return [
            permission()
            for permission in permission_classes.get(self.action, [permissions.IsAdminUser])
        ]


    def create(self, request):
        """
        Create a new filled madlib.

        Expected JSON:
        {
            "template_id": "507f1f77bcf86cd799439011",
            "creator_id": "507f1f77bcf86cd799439012",
            "inputted_blanks": [
                {"id": "1", "input": "sing"},
                {"id": "2", "input": "running"}
            ]
        }
        """
        if not request.user.is_authenticated:
            logger.warning("Unauthenticated user attempted to create filled madlib")
            return Response({'error': 'Not authenticated'})
        try:
            data = request.data
            logger.debug(f"Creating filled madlib for user: {request.user.id}")

            # Validate required fields
            required_fields = ['template_id', 'creator_id', 'inputted_blanks']
            if not all(field in data for field in required_fields):
                logger.warning("Missing required fields in create filled madlib request")
                return Response(
                    {'error': f'Missing required fields: {required_fields}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate inputted_blanks is a list
            if not isinstance(data['inputted_blanks'], list):
                logger.warning("inputted_blanks is not a list in create filled madlib request")
                return Response(
                    {'error': 'inputted_blanks must be a list'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            madlib_id = self.madlibs_service.new_filled_madlib(
                template_id=data['template_id'],
                creator_id=data['creator_id'],
                inputted_blanks=data['inputted_blanks']
            )

            if not madlib_id:
                logger.error("Failed to create filled madlib")
                return Response(
                    {'error': 'Failed to create madlib'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            logger.info(f"Filled madlib created: {madlib_id}")
            return Response(
                {'id': madlib_id, 'message': 'Madlib created successfully'},
                status=status.HTTP_201_CREATED
            )

        except InvalidId:
            logger.warning("Invalid template_id or creator_id format in create filled madlib")
            return Response(
                {'error': 'Invalid template_id or creator_id format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating filled madlib: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """
        Retrieve a filled madlib by ID.

        GET /api/madlibs/{id}/
        """
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'})
        if not pk:
            return Response(
                {'error': 'No data provided for update'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            madlib = self.madlibs_service.get_by_id(str(pk))

            if not madlib:
                return Response(
                    {'error': 'Madlib not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(madlib, status=status.HTTP_200_OK)

        except InvalidId:
            return Response(
                {'error': 'Invalid madlib ID format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        """
        Update a filled madlib's content and timestamp.

        Expected JSON:
        {
            "inputted_blanks": [
                {"id": "1", "input": "dance"},
                {"id": "2", "input": "jumping"}
            ]
        }
        """
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'})
        try:
            data = request.data

            if 'inputted_blanks' not in data:
                return Response(
                    {'error': 'inputted_blanks field is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not isinstance(data['inputted_blanks'], list):
                return Response(
                    {'error': 'inputted_blanks must be a list'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            success = self.madlibs_service.update_filled_madlib(
                filled_madlib_id=str(pk),
                inputted_blanks=data['inputted_blanks']
            )

            if not success:
                return Response(
                    {'error': 'Madlib not found or update failed'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {'message': 'Madlib updated successfully'},
                status=status.HTTP_200_OK
            )

        except InvalidId:
            return Response(
                {'error': 'Invalid madlib ID format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """
        Delete a filled madlib.

        DELETE /api/madlibs/{id}/
        """
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'})
        if not pk:
            return Response(
                {'error': 'No data provided for update'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            success = self.madlibs_service.delete_filled_madlib(str(pk))

            if not success:
                return Response(
                    {'error': 'Madlib not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {'message': 'Madlib deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )

        except InvalidId:
            return Response(
                {'error': 'Invalid madlib ID format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def by_creator(self, request):
        """
        Get all madlibs created by a specific user.

        GET /api/madlibs/by_creator/?creator_id={creator_id}
        """
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'})
        try:
            creator_id = request.query_params.get('creator_id')

            if not creator_id:
                return Response(
                    {'error': 'creator_id query parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            madlibs = self.madlibs_service.get_by_creator(creator_id)

            return Response(madlibs, status=status.HTTP_200_OK)

        except InvalidId:
            return Response(
                {'error': 'Invalid creator_id format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )