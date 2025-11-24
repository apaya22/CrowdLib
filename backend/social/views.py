from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import UserOperations
from .models import LikeModel, CommentModel
import logging
from bson import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)

class LikeViewSet(viewsets.ViewSet):
    """
    API endpoints for liking/unliking posts and comments.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.like_service = LikeModel()
        self.comment_service = CommentModel()
        self.user_service = UserOperations()

    def get_permissions(self):
        """
        Permission mapping per action
        """
        permission_classes = {
            'like_post': [permissions.IsAuthenticated],
            'unlike_post': [permissions.IsAuthenticated],
            'user_liked_post': [permissions.IsAuthenticated],
            'like_comment': [permissions.IsAuthenticated],
            'unlike_comment': [permissions.IsAuthenticated],

            # Public
            'get_post_likes_count': [permissions.AllowAny],
        }

        return [
            permission()
            for permission in permission_classes.get(self.action, [permissions.IsAdminUser])
        ]

    # -------------------------------------------------------------------------
    # POST LIKE A POST
    # -------------------------------------------------------------------------
    @action(detail=True, methods=['post'], url_path='like')
    def like_post(self, request, pk=None):
        """
        Like a post.
        POST /api/posts/{id}/like/
        """
        try:
            mongo_user = self.user_service.get_by_email(request.user.email)
            if not mongo_user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            user_id = mongo_user['_id']
            post_id = pk

            if self.like_service.user_liked_post(user_id, post_id):
                return Response({'message': 'Post already liked.'}, status=status.HTTP_200_OK)

            like_id = self.like_service.like_post(user_id, post_id)
            logger.info(f"User {user_id} liked post {post_id}")

            return Response(
                {'like_id': str(like_id), 'message': 'Post liked successfully.'},
                status=status.HTTP_201_CREATED
            )

        except InvalidId:
            return Response({'error': 'Invalid post ID.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error liking post: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # -------------------------------------------------------------------------
    # POST UNLIKE A POST
    # -------------------------------------------------------------------------
    @action(detail=True, methods=['post'], url_path='unlike')
    def unlike_post(self, request, pk=None):
        """
        Unlike a post.
        POST /api/posts/{id}/unlike/
        """
        try:
            mongo_user = self.user_service.get_by_email(request.user.email)
            if not mongo_user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            user_id = mongo_user['_id']
            post_id = pk

            success = self.like_service.unlike_post(user_id, post_id)
            if not success:
                return Response({'message': 'Like not found.'}, status=status.HTTP_404_NOT_FOUND)

            logger.info(f"User {user_id} unliked post {post_id}")
            return Response({'message': 'Post unliked successfully.'}, status=status.HTTP_200_OK)

        except InvalidId:
            return Response({'error': 'Invalid post ID.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error unliking post: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # -------------------------------------------------------------------------
    # GET LIKE COUNT FOR A POST
    # -------------------------------------------------------------------------
    @action(detail=True, methods=['get'], url_path='count')
    def get_post_likes_count(self, request, pk=None):
        """
        Get the number of likes on a post.
        GET /api/posts/{id}/count/
        """
        try:
            count = self.like_service.get_post_likes_count(pk)
            return Response({'post_id': pk, 'likes_count': count}, status=status.HTTP_200_OK)

        except InvalidId:
            return Response({'error': 'Invalid post ID.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error getting like count: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # -------------------------------------------------------------------------
    # GET IF USER LIKED POST
    # -------------------------------------------------------------------------
    @action(detail=True, methods=['get'], url_path='liked')
    def user_liked_post(self, request, pk=None):
        """
        Check whether the authenticated user liked a post.
        GET /api/posts/{id}/liked/
        """
        try:
            mongo_user = self.user_service.get_by_email(request.user.email)
            if not mongo_user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            user_id = mongo_user['_id']
            liked = self.like_service.user_liked_post(user_id, pk)

            return Response({'liked': liked}, status=status.HTTP_200_OK)

        except InvalidId:
            return Response({'error': 'Invalid post ID.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error checking liked status: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # -------------------------------------------------------------------------
    # LIKE A COMMENT
    # -------------------------------------------------------------------------
    @action(detail=False, methods=['post'], url_path='comments/(?P<comment_id>[^/.]+)/like')
    def like_comment(self, request, comment_id=None):
        """
        Like a comment.
        POST /api/posts/comments/{comment_id}/like/
        """
        try:
            mongo_user = self.user_service.get_by_email(request.user.email)
            if not mongo_user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            user_id = mongo_user['_id']

            like_id = self.like_service.like_comment(user_id, comment_id)
            logger.info(f"User {user_id} liked comment {comment_id}")

            return Response(
                {'like_id': str(like_id), 'message': 'Comment liked successfully.'},
                status=status.HTTP_201_CREATED
            )

        except InvalidId:
            return Response({'error': 'Invalid comment ID.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error liking comment: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # -------------------------------------------------------------------------
    # UNLIKE A COMMENT
    # -------------------------------------------------------------------------
    @action(detail=False, methods=['post'], url_path='comments/(?P<comment_id>[^/.]+)/unlike')
    def unlike_comment(self, request, comment_id=None):
        """
        Unlike a comment.
        POST /api/posts/comments/{comment_id}/unlike/
        """
        try:
            mongo_user = self.user_service.get_by_email(request.user.email)
            if not mongo_user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            user_id = mongo_user['_id']

            success = self.like_service.unlike_comment(user_id, comment_id)
            if not success:
                return Response({'message': 'Like not found.'}, status=status.HTTP_404_NOT_FOUND)

            logger.info(f"User {user_id} unliked comment {comment_id}")
            return Response({'message': 'Comment unliked successfully.'}, status=status.HTTP_200_OK)

        except InvalidId:
            return Response({'error': 'Invalid comment ID.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error unliking comment: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# comments 
class CommentViewSet(viewsets.ViewSet):
    """
    API endpoints for comments.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.comment_service = CommentModel()
        self.user_service = UserOperations()

    def get_permissions(self):
        permission_classes = {
            'create_comment': [permissions.IsAuthenticated],
            'update': [permissions.IsAuthenticated],
            'destroy': [permissions.IsAuthenticated],
            
            # Public
            'list_post_comments': [permissions.AllowAny],
            'retrieve': [permissions.AllowAny],
        }

        return [
            permission()
            for permission in permission_classes.get(self.action, [permissions.IsAdminUser])
        ]

    
    # CREATE COMMENT
    # POST /api/posts/{post_id}/comments/
    @action(detail=True, methods=['post'], url_path='comment')
    def create_comment(self, request, pk=None):
        try:
            # get Mongo user
            mongo_user = self.user_service.get_by_email(request.user.email)
            if not mongo_user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            user_id = mongo_user["_id"]
            post_id = pk
            text = request.data.get("text", "").strip()

            if not text:
                return Response({'error': 'text field is required'}, status=status.HTTP_400_BAD_REQUEST)

            comment_id = self.comment_service.add_comment(user_id, post_id, text)

            return Response(
                {'comment_id': str(comment_id), 'message': 'Comment created successfully'},
                status=status.HTTP_201_CREATED
            )

        except InvalidId:
            return Response({'error': 'Invalid post ID'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating comment: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # GET ALL COMMENTS FOR A POST
    # GET /api/posts/{post_id}/comments/
    @action(detail=True, methods=['get'], url_path='comments')
    def list_post_comments(self, request, pk=None):
        try:
            comments = self.comment_service.get_post_comments(pk)
            return Response({'post_id': pk, 'comments': comments}, status=status.HTTP_200_OK)

        except InvalidId:
            return Response({'error': 'Invalid post ID'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error retrieving comments: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # RETRIEVE A SINGLE COMMENT
    # GET /api/comments/{comment_id}/
    def retrieve(self, request, pk=None):
        try:
            comment = self.comment_service.collection.find_one({"_id": ObjectId(pk)})

            if not comment:
                return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

            comment['_id'] = str(comment['_id'])
            comment['user_id'] = str(comment['user_id'])
            comment['post_id'] = str(comment['post_id'])

            return Response(comment, status=status.HTTP_200_OK)

        except InvalidId:
            return Response({'error': 'Invalid comment ID'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error retrieving comment: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # UPDATE COMMENT
    # PUT /api/comments/{id}/
    def update(self, request, pk=None):
        try:
            mongo_user = self.user_service.get_by_email(request.user.email)
            if not mongo_user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            user_id = mongo_user["_id"]

            new_text = request.data.get("text", "").strip()
            if not new_text:
                return Response({'error': 'text field is required'}, status=status.HTTP_400_BAD_REQUEST)

            comment = self.comment_service.collection.find_one({"_id": ObjectId(pk)})
            if not comment:
                return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

            # Ownership check
            if str(comment["user_id"]) != str(user_id):
                return Response(
                    {'error': 'You can only update your own comments'},
                    status=status.HTTP_403_FORBIDDEN
                )

            self.comment_service.collection.update_one(
                {"_id": ObjectId(pk)},
                {"$set": {"text": new_text}}
            )

            return Response({'message': 'Comment updated successfully'}, status=status.HTTP_200_OK)

        except InvalidId:
            return Response({'error': 'Invalid comment ID'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating comment: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # DELETE COMMENT
    # DELETE /api/comments/{id}/
    def destroy(self, request, pk=None):
        try:
            mongo_user = self.user_service.get_by_email(request.user.email)
            if not mongo_user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            user_id = mongo_user["_id"]

            comment = self.comment_service.collection.find_one({"_id": ObjectId(pk)})
            if not comment:
                return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

            # Ownership check
            if str(comment["user_id"]) != str(user_id):
                return Response(
                    {'error': 'You can only delete your own comments'},
                    status=status.HTTP_403_FORBIDDEN
                )

            self.comment_service.collection.delete_one({"_id": ObjectId(pk)})

            return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        except InvalidId:
            return Response({'error': 'Invalid comment ID'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error deleting comment: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)