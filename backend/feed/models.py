from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict
from core.db_connect import get_collection
import logging

logger = logging.getLogger(__name__)


class FeedService:
    """
    Service for managing feed operations and aggregations.

    Provides methods to retrieve UserFilledMadlibs sorted by:
    - Like count (top-liked)
    - Created date (most recent)
    - Comment count (most discussed)

    All methods support time filtering and pagination.
    """

    def __init__(self):
        self.filled_madlibs_coll = get_collection('filled_madlibs')
        self.likes_coll = get_collection('likes')
        self.comments_coll = get_collection('comments')
        self.users_coll = get_collection('users')
        self.templates_coll = get_collection('story_templates')
        self._create_indexes()

    def _create_indexes(self):
        """
        Create database indexes for efficient feed queries.
        Called automatically during initialization.
        """
        try:
            logger.debug("Creating feed-related indexes")

            # filled_madlibs indexes
            self.filled_madlibs_coll.create_index([("created_at", -1)])
            self.filled_madlibs_coll.create_index([("public", 1), ("created_at", -1)])
            self.filled_madlibs_coll.create_index([("creator_id", 1)])

            # likes indexes
            self.likes_coll.create_index([("post_id", 1), ("comment_id", 1)])

            # comments indexes
            self.comments_coll.create_index([("post_id", 1), ("created_at", -1)])

            logger.info("Feed indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating feed indexes: {e}")

    def _build_time_filter(self, time_filter: Optional[str]) -> Dict:
        """
        Build MongoDB time filter query.

        Args:
            time_filter: One of 'day', 'week', 'month', 'year', 'all' (default)

        Returns:
            Dictionary with created_at filter or empty dict
        """
        if not time_filter or time_filter == 'all':
            return {}

        now = datetime.now(timezone.utc)
        filter_map = {
            'day': now - timedelta(days=1),
            'week': now - timedelta(weeks=1),
            'month': now - timedelta(days=30),
            'year': now - timedelta(days=365)
        }

        if time_filter in filter_map:
            return {"created_at": {"$gte": filter_map[time_filter]}}

        return {}

    def _convert_objectids(self, doc: Dict) -> Dict:
        """
        Convert ObjectIds to strings for JSON serialization.

        Args:
            doc: MongoDB document

        Returns:
            Document with ObjectIds converted to strings
        """
        if doc:
            if '_id' in doc and isinstance(doc['_id'], ObjectId):
                doc['_id'] = str(doc['_id'])
            if 'template_id' in doc and isinstance(doc['template_id'], ObjectId):
                doc['template_id'] = str(doc['template_id'])
            if 'creator_id' in doc and isinstance(doc['creator_id'], ObjectId):
                doc['creator_id'] = str(doc['creator_id'])
        return doc

    def get_top_by_likes(self, limit: int = 50, offset: int = 0, time_filter: Optional[str] = 'all') -> List[Dict]:
        """
        Get UserFilledMadlibs sorted by like count (descending).
        Ties broken by created_at (most recent first).

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip for pagination
            time_filter: Time filter ('day', 'week', 'month', 'year', 'all')

        Returns:
            List of enriched madlib documents with likes_count, comments_count,
            creator_username, and template_title
        """
        try:
            logger.debug(f"Getting top liked feed: limit={limit}, offset={offset}, time_filter={time_filter}")

            time_filter_query = self._build_time_filter(time_filter)
            match_query = {"public": True}
            if time_filter_query:
                match_query.update(time_filter_query)

            pipeline = [
                {"$match": match_query},
                # Lookup likes count
                {"$lookup": {
                    "from": "likes",
                    "let": {"madlib_id": "$_id"},
                    "pipeline": [
                        {"$match": {
                            "$expr": {"$eq": ["$post_id", "$$madlib_id"]},
                            "comment_id": None
                        }},
                        {"$count": "count"}
                    ],
                    "as": "like_stats"
                }},
                # Lookup comments count
                {"$lookup": {
                    "from": "comments",
                    "let": {"madlib_id": "$_id"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$post_id", "$$madlib_id"]}}},
                        {"$count": "count"}
                    ],
                    "as": "comment_stats"
                }},
                # Lookup creator info
                {"$lookup": {
                    "from": "users",
                    "localField": "creator_id",
                    "foreignField": "_id",
                    "as": "creator_info"
                }},
                # Lookup template info
                {"$lookup": {
                    "from": "story_templates",
                    "localField": "template_id",
                    "foreignField": "_id",
                    "as": "template_info"
                }},
                {"$addFields": {
                    "likes_count": {"$ifNull": [{"$arrayElemAt": ["$like_stats.count", 0]}, 0]},
                    "comments_count": {"$ifNull": [{"$arrayElemAt": ["$comment_stats.count", 0]}, 0]},
                    "creator_username": {"$arrayElemAt": ["$creator_info.username", 0]},
                    "template_title": {"$arrayElemAt": ["$template_info.title", 0]}
                }},
                {"$project": {
                    "like_stats": 0,
                    "comment_stats": 0,
                    "creator_info": 0,
                    "template_info": 0
                }},
                {"$sort": {"likes_count": -1, "created_at": -1}},
                {"$skip": offset},
                {"$limit": limit}
            ]

            results = list(self.filled_madlibs_coll.aggregate(pipeline))

            # Convert ObjectIds to strings
            for result in results:
                self._convert_objectids(result)

            logger.info(f"Retrieved {len(results)} top liked madlibs")
            return results

        except Exception as e:
            logger.error(f"Error getting top liked feed: {e}")
            return []

    def get_most_recent(self, limit: int = 50, offset: int = 0, time_filter: Optional[str] = 'all') -> List[Dict]:
        """
        Get UserFilledMadlibs sorted by created_at (descending).

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip for pagination
            time_filter: Time filter ('day', 'week', 'month', 'year', 'all')

        Returns:
            List of enriched madlib documents with likes_count, comments_count,
            creator_username, and template_title
        """
        try:
            logger.debug(f"Getting most recent feed: limit={limit}, offset={offset}, time_filter={time_filter}")

            time_filter_query = self._build_time_filter(time_filter)
            match_query = {"public": True}
            if time_filter_query:
                match_query.update(time_filter_query)

            pipeline = [
                {"$match": match_query},
                {"$sort": {"created_at": -1}},
                {"$skip": offset},
                {"$limit": limit},
                # Lookup likes count
                {"$lookup": {
                    "from": "likes",
                    "let": {"madlib_id": "$_id"},
                    "pipeline": [
                        {"$match": {
                            "$expr": {"$eq": ["$post_id", "$$madlib_id"]},
                            "comment_id": None
                        }},
                        {"$count": "count"}
                    ],
                    "as": "like_stats"
                }},
                # Lookup comments count
                {"$lookup": {
                    "from": "comments",
                    "let": {"madlib_id": "$_id"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$post_id", "$$madlib_id"]}}},
                        {"$count": "count"}
                    ],
                    "as": "comment_stats"
                }},
                # Lookup creator info
                {"$lookup": {
                    "from": "users",
                    "localField": "creator_id",
                    "foreignField": "_id",
                    "as": "creator_info"
                }},
                # Lookup template info
                {"$lookup": {
                    "from": "story_templates",
                    "localField": "template_id",
                    "foreignField": "_id",
                    "as": "template_info"
                }},
                {"$addFields": {
                    "likes_count": {"$ifNull": [{"$arrayElemAt": ["$like_stats.count", 0]}, 0]},
                    "comments_count": {"$ifNull": [{"$arrayElemAt": ["$comment_stats.count", 0]}, 0]},
                    "creator_username": {"$arrayElemAt": ["$creator_info.username", 0]},
                    "template_title": {"$arrayElemAt": ["$template_info.title", 0]}
                }},
                {"$project": {
                    "like_stats": 0,
                    "comment_stats": 0,
                    "creator_info": 0,
                    "template_info": 0
                }}
            ]

            results = list(self.filled_madlibs_coll.aggregate(pipeline))

            # Convert ObjectIds to strings
            for result in results:
                self._convert_objectids(result)

            logger.info(f"Retrieved {len(results)} most recent madlibs")
            return results

        except Exception as e:
            logger.error(f"Error getting most recent feed: {e}")
            return []

    def get_most_discussed(self, limit: int = 50, offset: int = 0, time_filter: Optional[str] = 'all') -> List[Dict]:
        """
        Get UserFilledMadlibs sorted by comment count (descending).
        Ties broken by created_at (most recent first).

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip for pagination
            time_filter: Time filter ('day', 'week', 'month', 'year', 'all')

        Returns:
            List of enriched madlib documents with likes_count, comments_count,
            creator_username, and template_title
        """
        try:
            logger.debug(f"Getting most discussed feed: limit={limit}, offset={offset}, time_filter={time_filter}")

            time_filter_query = self._build_time_filter(time_filter)
            match_query = {"public": True}
            if time_filter_query:
                match_query.update(time_filter_query)

            pipeline = [
                {"$match": match_query},
                # Lookup likes count
                {"$lookup": {
                    "from": "likes",
                    "let": {"madlib_id": "$_id"},
                    "pipeline": [
                        {"$match": {
                            "$expr": {"$eq": ["$post_id", "$$madlib_id"]},
                            "comment_id": None
                        }},
                        {"$count": "count"}
                    ],
                    "as": "like_stats"
                }},
                # Lookup comments count
                {"$lookup": {
                    "from": "comments",
                    "let": {"madlib_id": "$_id"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$post_id", "$$madlib_id"]}}},
                        {"$count": "count"}
                    ],
                    "as": "comment_stats"
                }},
                # Lookup creator info
                {"$lookup": {
                    "from": "users",
                    "localField": "creator_id",
                    "foreignField": "_id",
                    "as": "creator_info"
                }},
                # Lookup template info
                {"$lookup": {
                    "from": "story_templates",
                    "localField": "template_id",
                    "foreignField": "_id",
                    "as": "template_info"
                }},
                {"$addFields": {
                    "likes_count": {"$ifNull": [{"$arrayElemAt": ["$like_stats.count", 0]}, 0]},
                    "comments_count": {"$ifNull": [{"$arrayElemAt": ["$comment_stats.count", 0]}, 0]},
                    "creator_username": {"$arrayElemAt": ["$creator_info.username", 0]},
                    "template_title": {"$arrayElemAt": ["$template_info.title", 0]}
                }},
                {"$project": {
                    "like_stats": 0,
                    "comment_stats": 0,
                    "creator_info": 0,
                    "template_info": 0
                }},
                {"$sort": {"comments_count": -1, "created_at": -1}},
                {"$skip": offset},
                {"$limit": limit}
            ]

            results = list(self.filled_madlibs_coll.aggregate(pipeline))

            # Convert ObjectIds to strings
            for result in results:
                self._convert_objectids(result)

            logger.info(f"Retrieved {len(results)} most discussed madlibs")
            return results

        except Exception as e:
            logger.error(f"Error getting most discussed feed: {e}")
            return []
