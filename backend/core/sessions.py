from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.utils import timezone
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SessionStore(SessionBase):
    def __init__(self, session_key=None):
        super().__init__(session_key)
        from core.db_connect import get_collection
        self.collection = get_collection('sessions')

    def create(self):
        """Creates a new session key"""
        while True:
            self._session_key = self._get_new_session_key() # type: ignore
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        """Save the current session data to MongoDB"""
        if self.session_key is None:
            return self.create()

        # Encode session data as Django expects
        # Access session data through dict() to get all current session data
        session_dict = dict(self.items())
        encoded_data = self.encode(session_dict)

        logger.debug(f"Saving session: key={self.session_key}")
        logger.debug(f"Session data keys: {list(session_dict.keys())}")
        logger.debug(f"Must create: {must_create}")

        if must_create:
            # Check if session already exists
            if self.exists(self.session_key):
                logger.error(f"Session already exists: {self.session_key}")
                raise CreateError

        session_data = {
            'session_key': self.session_key,
            'session_data': encoded_data,
            'expire_date': self.get_expiry_date()
        }

        if must_create:
            # Insert new session
            result = self.collection.insert_one(session_data)
            logger.info(f"Session created: key={self.session_key}, inserted_id={result.inserted_id}")
        else:
            # Update existing or create new session
            result = self.collection.update_one(
                {'session_key': self.session_key},
                {'$set': session_data},
                upsert=True
            )
            logger.info(f"Session saved: key={self.session_key}, matched={result.matched_count}, modified={result.modified_count}, upserted={result.upserted_id}")

    def exists(self, session_key):
        """Check if a session exists in the database"""
        return self.collection.find_one({'session_key': session_key}) is not None

    def load(self):
        """Load session data from MongoDB"""
        logger.debug(f"Loading session: key={self.session_key}")

        if self.session_key is None:
            logger.debug("No session key provided, returning empty dict")
            return {}

        session_doc = self.collection.find_one({'session_key': self.session_key})
        logger.debug(f"Session document found: {session_doc is not None}")

        if session_doc:
            expire_date = session_doc.get('expire_date')
            # Check if session has expired
            if expire_date:
                # Make expire_date timezone-aware if it isn't already
                if isinstance(expire_date, datetime) and expire_date.tzinfo is None:
                    expire_date = timezone.make_aware(expire_date)

                now = timezone.now()
                logger.debug(f"Expire date: {expire_date}, Current time: {now}")

                if expire_date > now:
                    encoded_data = session_doc.get('session_data', '')
                    try:
                        decoded = self.decode(encoded_data)
                        logger.info(f"Session loaded successfully: key={self.session_key}, data_keys={list(decoded.keys())}")
                        return decoded
                    except Exception as e:
                        # If decoding fails, return empty dict
                        logger.error(f"Failed to decode session: key={self.session_key}, error={e}")
                        return {}
                else:
                    logger.info(f"Session expired: key={self.session_key}, expiry={expire_date}")

        # Session doesn't exist or is expired
        self._session_key = None
        logger.debug(f"Session not found or expired: key={self.session_key}")
        return {}

    def delete(self, session_key=None):
        """Delete a session from the database"""
        key = session_key or self.session_key
        if key:
            self.collection.delete_one({'session_key': key})
            if session_key is None:
                # Clear the current session
                self._session_key = None

    @classmethod
    def clear_expired(cls):
        """Remove expired sessions from the database"""
        from core.db_connect import get_collection
        collection = get_collection('sessions')
        collection.delete_many({'expire_date': {'$lt': timezone.now()}})
