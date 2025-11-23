# backend/social/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, Mock
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from bson import ObjectId

# Import the viewset module path used by your project
# The tests patch classes inside social.views, so ensure that is correct for your codebase
# from social.views import LikeViewSet, CommentViewSet   <-- not needed directly here

User = get_user_model()

# -------------------------
# LikeViewSet API tests
# -------------------------
class LikeViewSetAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="tester", password="pass", email="tester@example.com")

        # Example mongo-like user id string to be returned from mock UserOperations.get_by_email
        self.mongo_user_id = str(ObjectId())

    # Helper to make endpoint path consistent with your router setup:
    def _like_post_url(self, post_id):
        # Matches action detail route: /api/likes/{pk}/like/
        return f"/api/likes/{post_id}/like/"

    def _unlike_post_url(self, post_id):
        return f"/api/likes/{post_id}/unlike/"

    def _count_url(self, post_id):
        return f"/api/likes/{post_id}/count/"

    # ---------------------------------------------------------------------
    @patch('social.views.LikeModel')
    @patch('social.views.UserOperations')
    def test_like_post_unauthenticated(self, MockUserOps, MockLikeModel):
        """Unauthenticated clients should be rejected (403 or 401)"""
        url = self._like_post_url("123")
        resp = self.client.post(url)
        # DRF commonly returns 403 when permission classes require auth
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    # ---------------------------------------------------------------------
    @patch('social.views.LikeModel')
    @patch('social.views.UserOperations')
    def test_like_post_success(self, MockUserOps, MockLikeModel):
        """Authenticated user can like a post (first time)"""
        # Arrange: mock user lookup and like service
        svc_like = MockLikeModel.return_value
        svc_like.user_liked_post.return_value = False
        svc_like.like_post.return_value = "mock-like-id"

        user_ops = MockUserOps.return_value
        user_ops.get_by_email.return_value = {'_id': self.mongo_user_id}

        self.client.force_authenticate(user=self.user)
        url = self._like_post_url("post-abc")

        resp = self.client.post(url)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('like_id', resp.data)
        self.assertEqual(resp.data['message'], 'Post liked successfully.')
        svc_like.user_liked_post.assert_called_once_with(self.mongo_user_id, 'post-abc')
        svc_like.like_post.assert_called_once_with(self.mongo_user_id, 'post-abc')

    # ---------------------------------------------------------------------
    @patch('social.views.LikeModel')
    @patch('social.views.UserOperations')
    def test_like_post_already_liked(self, MockUserOps, MockLikeModel):
        """If user already liked the post, return 200 with message"""
        svc_like = MockLikeModel.return_value
        svc_like.user_liked_post.return_value = True

        user_ops = MockUserOps.return_value
        user_ops.get_by_email.return_value = {'_id': self.mongo_user_id}

        self.client.force_authenticate(user=self.user)
        url = self._like_post_url("post-abc")

        resp = self.client.post(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['message'], 'Post already liked.')
        svc_like.user_liked_post.assert_called_once_with(self.mongo_user_id, 'post-abc')

    # ---------------------------------------------------------------------
    @patch('social.views.LikeModel')
    @patch('social.views.UserOperations')
    def test_unlike_post_success(self, MockUserOps, MockLikeModel):
        """Authenticated user can unlike a previously liked post"""
        svc_like = MockLikeModel.return_value
        svc_like.unlike_post.return_value = True

        user_ops = MockUserOps.return_value
        user_ops.get_by_email.return_value = {'_id': self.mongo_user_id}

        self.client.force_authenticate(user=self.user)
        url = self._unlike_post_url("post-abc")

        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['message'], 'Post unliked successfully.')
        svc_like.unlike_post.assert_called_once_with(self.mongo_user_id, 'post-abc')

    # ---------------------------------------------------------------------
    @patch('social.views.LikeModel')
    def test_get_post_likes_count_public(self, MockLikeModel):
        """get_post_likes_count should be publicly accessible (no auth)"""
        svc_like = MockLikeModel.return_value
        svc_like.get_post_likes_count.return_value = 5

        url = self._count_url("post-abc")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # the view returns 'likes_count' in the code above
        self.assertEqual(resp.data['likes_count'], 5)
        svc_like.get_post_likes_count.assert_called_once_with('post-abc')

    # ---------------------------------------------------------------------
    @patch('social.views.LikeModel')
    @patch('social.views.UserOperations')
    def test_like_comment_and_unlike_comment(self, MockUserOps, MockLikeModel):
        """Test liking and unliking a comment endpoints"""
        svc_like = MockLikeModel.return_value
        svc_like.like_comment.return_value = "mock-like-comment-id"
        svc_like.unlike_comment.return_value = True

        user_ops = MockUserOps.return_value
        user_ops.get_by_email.return_value = {'_id': self.mongo_user_id}

        self.client.force_authenticate(user=self.user)
        like_url = "/api/likes/comments/COMMENT123/like/"
        unlike_url = "/api/likes/comments/COMMENT123/unlike/"

        resp_like = self.client.post(like_url)
        self.assertEqual(resp_like.status_code, status.HTTP_201_CREATED)
        self.assertIn('like_id', resp_like.data)
        svc_like.like_comment.assert_called_once_with(self.mongo_user_id, 'COMMENT123')

        resp_unlike = self.client.post(unlike_url)
        self.assertEqual(resp_unlike.status_code, status.HTTP_200_OK)
        svc_like.unlike_comment.assert_called_once_with(self.mongo_user_id, 'COMMENT123')


# -------------------------
# CommentViewSet API tests
# -------------------------
class CommentViewSetAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="commenter", password="pass", email="commenter@example.com")
        self.mongo_user_id = str(ObjectId())

    def _create_comment_url(self, post_id):
        return f"/api/comments/{post_id}/comment/"

    def _list_comments_url(self, post_id):
        return f"/api/comments/{post_id}/comments/"

    def _retrieve_comment_url(self, comment_id):
        return f"/api/comments/{comment_id}/"

    # ---------------------------------------------------------------------
    @patch('social.views.CommentModel')
    @patch('social.views.UserOperations')
    def test_create_comment_success(self, MockUserOps, MockCommentModel):
        svc_comment = MockCommentModel.return_value
        svc_comment.add_comment.return_value = "mock-comment-id"

        user_ops = MockUserOps.return_value
        user_ops.get_by_email.return_value = {'_id': self.mongo_user_id}

        self.client.force_authenticate(user=self.user)
        url = self._create_comment_url("POST123")
        resp = self.client.post(url, data={"text": "Nice post!"}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('comment_id', resp.data)
        svc_comment.add_comment.assert_called_once_with(self.mongo_user_id, 'POST123', 'Nice post!')

    # ---------------------------------------------------------------------
    @patch('social.views.UserOperations')
    def test_create_comment_missing_text(self, MockCommentModel):
        self.client.force_authenticate(user=self.user)
        url = self._create_comment_url("POST123")
        resp = self.client.post(url, data={"text": "   "}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------------------
    @patch('social.views.CommentModel')
    def test_list_post_comments_public(self, MockCommentModel):
        svc_comment = MockCommentModel.return_value
        svc_comment.get_post_comments.return_value = [
            {"_id": str(ObjectId()), "user_id": str(ObjectId()), "post_id": "POST123", "text": "A", "created_at": "t"},
            {"_id": str(ObjectId()), "user_id": str(ObjectId()), "post_id": "POST123", "text": "B", "created_at": "t"}
        ]

        url = self._list_comments_url("POST123")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('comments', resp.data)
        self.assertEqual(len(resp.data['comments']), 2)
        svc_comment.get_post_comments.assert_called_once_with('POST123')

    # ---------------------------------------------------------------------
    @patch('social.views.CommentModel')
    def test_retrieve_comment(self, MockCommentModel):
        svc_comment = MockCommentModel.return_value
        # Simulate collection.find_one returning a document
        fake_comment_id = str(ObjectId())
        svc_comment.collection.find_one.return_value = {
            "_id": ObjectId(fake_comment_id),
            "user_id": ObjectId(self.mongo_user_id),
            "post_id": ObjectId("507f1f77bcf86cd799439000"),
            "text": "Hello",
            "created_at": "t"
        }

        url = self._retrieve_comment_url(fake_comment_id)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['text'], 'Hello')

    # ---------------------------------------------------------------------
    @patch('social.views.CommentModel')
    @patch('social.views.UserOperations')
    def test_update_and_delete_comment_with_ownership(self, MockUserOps, MockCommentModel):
        svc_comment = MockCommentModel.return_value
        user_ops = MockUserOps.return_value
        user_ops.get_by_email.return_value = {'_id': self.mongo_user_id}

        # Prepare existing comment owned by the mongo_user_id
        fake_comment_id = str(ObjectId())
        svc_comment.collection.find_one.return_value = {
            "_id": ObjectId(fake_comment_id),
            "user_id": ObjectId(self.mongo_user_id),
            "post_id": ObjectId("507f1f77bcf86cd799439000"),
            "text": "Old text",
            "created_at": "t"
        }

        self.client.force_authenticate(user=self.user)

        # Update comment
        update_url = self._retrieve_comment_url(fake_comment_id)
        resp_update = self.client.put(update_url, data={"text": "New text"}, format='json')
        self.assertEqual(resp_update.status_code, status.HTTP_200_OK)
        svc_comment.collection.update_one.assert_called_once()

        # Delete comment
        resp_delete = self.client.delete(update_url)
        self.assertIn(resp_delete.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK])
        svc_comment.collection.delete_one.assert_called()

