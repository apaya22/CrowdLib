from bson.objectid import ObjectId
from datetime import datetime
from core.db_connect import get_collection


class LikeModel:
    """Handle likes and comments operations"""
    def __init__(self):
        self.collection = get_collection('likes')
        self._create_index()
        
    def _create_index(self):
        self.collection.create_index([("user_id", 1)])
        self.collection.create_index([("post_id", 1)])
        self.collection.create_index([("comment_id", 1)])
        
    def like_post(self, user_id, post_id):
        """Add a like to a post"""
        like_doc = {
            "user_id": ObjectId(user_id),
            "post_id": ObjectId(post_id),
            "comment_id": None,
            "created_at": datetime.now()
        }
        return self.collection.insert_one(like_doc).inserted_id

    def like_comment(self, user_id, comment_id):
        """Add a like to a comment"""
        like_doc = {
            "user_id": ObjectId(user_id),
            "post_id": None,
            "comment_id": ObjectId(comment_id),
            "created_at": datetime.now()
        }
        return self.collection.insert_one(like_doc).inserted_id

    def get_post_likes_count(self, post_id):
        """Count likes on a post"""
        return self.collection.count_documents({
            "post_id": ObjectId(post_id),
            "comment_id": None
        })

    def user_liked_post(self, user_id, post_id):
        """Check if user already liked a post"""
        return self.collection.find_one({
            "user_id": ObjectId(user_id),
            "post_id": ObjectId(post_id),
            "comment_id": None
        }) is not None

class CommentModel:
    def __init__(self):
        self.collection = get_collection('comments')
        self._create_index()
        
    def _create_index(self):
        self.collection.create_index([("post_id", 1)])
        self.collection.create_index([("user_id", 1)])    
        
    def add_comment(self, user_id, post_id, text):
        """Add a comment to a post"""
        comment_doc = {
            "user_id": ObjectId(user_id),
            "post_id": ObjectId(post_id),
            "text": text,
            "created_at": datetime.now(),
            "likes_count": 0
        }
        return self.collection.insert_one(comment_doc).inserted_id

    def get_post_comments(self, post_id):
        """Retrieve all comments for a post"""
        return list(self.collection.find(
            {"post_id": ObjectId(post_id)},
            sort=[("created_at", -1)]
        ))
