from bson import ObjectId
from typing import Optional, List, Dict
from datetime import datetime, timezone
from core.db_connect import get_collection
import logging

logger = logging.getLogger(__name__)

class MadLibTemplate:
    def __init__(self):
        self.collection = get_collection('story_templates')
        self.create_indexs()
        
    def create_indexs(self):
        self.collection.create_index([('title', 1)])


    def get_by_id(self, madlib_id: str) -> Optional[Dict]:
        """
        Retrieve a madlib by MongoDB ObjectId

        Args:
            madlib_id: String representation of MongoDB ObjectId

        Returns:
            Dictionary containing the madlib or None if not found
        """
        try:
            logger.debug(f"Retrieving madlib by ID: {madlib_id}")
            result = self.collection.find_one({'_id': ObjectId(madlib_id)})
            if result:
                result['_id'] = str(result['_id'])  # Convert ObjectId to string
                logger.info(f"Madlib found: {madlib_id}")
            else:
                logger.info(f"Madlib not found: {madlib_id}")
            return result
        except Exception as e:
            logger.error(f"Error retrieving madlib by ID {madlib_id}: {e}")
            return None


    def search_by_title(self, title: str, exact: bool = False) -> List[Dict]:
        """
        Search for madlibs by title

        Args:
            title: Title to search for
            exact: If True, performs exact match; if False, performs case-insensitive partial match

        Returns:
            List of matching madlibs
        """
        try:
            logger.debug(f"Searching madlibs by title: '{title}' (exact={exact})")
            if exact:
                query = {'title': title}
            else:
                # Case-insensitive regex search
                query = {'title': {'$regex': title, '$options': 'i'}}

            results = list(self.collection.find(query))

            # Convert ObjectId to string for JSON serialization
            for result in results:
                if isinstance(result.get('_id'), ObjectId):
                    result['_id'] = str(result['_id'])

            logger.info(f"Search found {len(results)} madlibs matching '{title}'")
            return results
        except Exception as e:
            logger.error(f"Error searching madlibs by title '{title}': {e}")
            return []

    def get_all(self, limit: int = 100) -> List[Dict]:
        """
        Retrieve all madlibs with optional limit

        Args:
            limit: Maximum number of madlibs to retrieve

        Returns:
            List of all madlibs
        """
        try:
            logger.debug(f"Retrieving all madlibs (limit={limit})")
            results = list(self.collection.find().limit(limit))

            for result in results:
                if isinstance(result.get('_id'), ObjectId):
                    result['_id'] = str(result['_id'])

            logger.info(f"Retrieved {len(results)} madlibs")
            return results
        except Exception as e:
            logger.error(f"Error retrieving all madlibs: {e}")
            return []

    def create(self, madlib_data: Dict) -> Optional[str]:
        """
        Create a new madlib

        Args:
            madlib_data: Dictionary containing madlib data

        Returns:
            String ID of created madlib or None if failed
        """
        try:
            logger.debug(f"Creating new madlib with title: '{madlib_data.get('title', 'N/A')}'")
            result = self.collection.insert_one(madlib_data)
            logger.info(f"Madlib created: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating madlib: {e}")
            return None

    def update(self, madlib_id: str, update_data: Dict) -> bool:
        """
        Update an existing madlib

        Args:
            madlib_id: String representation of MongoDB ObjectId
            update_data: Dictionary containing fields to update

        Returns:
            True if update was successful, False otherwise
        """
        try:
            logger.debug(f"Updating madlib {madlib_id} with fields: {list(update_data.keys())}")
            result = self.collection.update_one(
                {'_id': ObjectId(madlib_id)},
                {'$set': update_data}
            )
            if result.modified_count > 0:
                logger.info(f"Madlib updated: {madlib_id}")
            else:
                logger.info(f"No changes made to madlib: {madlib_id}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating madlib {madlib_id}: {e}")
            return False

    def delete(self, madlib_id: str) -> bool:
        """
        Delete a madlib

        Args:
            madlib_id: String representation of MongoDB ObjectId

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            logger.debug(f"Deleting madlib: {madlib_id}")
            result = self.collection.delete_one({'_id': ObjectId(madlib_id)})
            if result.deleted_count > 0:
                logger.info(f"Madlib deleted: {madlib_id}")
            else:
                logger.info(f"Madlib not found: {madlib_id}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting madlib {madlib_id}: {e}")
            return False

class UserFilledMadlibs:
    def __init__(self):
        self.collection = get_collection('filled_madlibs')
        self._create_indexes()

    def _create_indexes(self):
        """
        Create database indexes for efficient filled madlib queries.
        Called automatically during initialization.
        """
        try:
            logger.debug("Creating filled madlib indexes")

            # MEDIUM: Template lookups (used in aggregations)
            self.collection.create_index([("template_id", 1)], name="idx_template_id")

            logger.info("Filled madlib indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating filled madlib indexes: {e}")

    def new_filled_madlib(self, template_id: str, creator_id: str, inputted_blanks: List[Dict]) -> Optional[str]:
        """
        Add a filled in madlib template to the database

        Args:
            template_id: String of MongoDB ObjectID to fill in
            creator_id: String of the user's MongoDB ObjectID 
            inputted_blanks: List of dicts with 'id' and 'input' keys

        Example of inputted_blanks:
            [
                {"id": "1", "input": "sing"},
                {"id": "2", "input": "running"},
                {"id": "3", "input": "creepy"}
            ]

        Returns:
            String ID of the new filled madlib or None if failed
        """
        try:
            logger.debug(f"Creating filled madlib: template_id={template_id}, creator_id={creator_id}, blanks_count={len(inputted_blanks)}")
            now = datetime.now(timezone.utc)

            madlib_data = {
                'template_id': ObjectId(template_id),
                'creator_id': ObjectId(creator_id),
                'created_at': now,
                'updated_at': now,
                'public': True,
                'content': inputted_blanks,  # Store the list of filled blanks
            }

            result = self.collection.insert_one(madlib_data)
            logger.info(f"Filled madlib created: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating filled madlib: template_id={template_id}, creator_id={creator_id}, error={e}")
            return None

    def update_filled_madlib(self, filled_madlib_id: str, inputted_blanks: List[Dict]) -> bool:
        """
        Update the filled blanks and modified time for a madlib

        Args:
            filled_madlib_id: String representation of MongoDB ObjectId
            inputted_blanks: Updated list of dicts with 'id' and 'input' keys

        Example of inputted_blanks:
            [
                {"id": "1", "input": "dance"},
                {"id": "2", "input": "jumping"}
            ]

        Returns:
            True if update was successful, False otherwise
        """
        try:
            logger.debug(f"Updating filled madlib {filled_madlib_id} with {len(inputted_blanks)} blanks")
            result = self.collection.update_one(
                {'_id': ObjectId(filled_madlib_id)},
                {'$set': {
                    'content': inputted_blanks,
                    'updated_at': datetime.now(timezone.utc)
                }}
            )
            if result.modified_count > 0:
                logger.info(f"Filled madlib updated: {filled_madlib_id}")
            else:
                logger.info(f"No changes made to filled madlib: {filled_madlib_id}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating filled madlib {filled_madlib_id}: {e}")
            return False

    def update_image_url(self, filled_madlib_id: str, image_url: str) -> bool:
        """
        Update the image URL for a filled madlib

        Args:
            filled_madlib_id: String representation of MongoDB ObjectId
            image_url: URL of the uploaded image

        Returns:
            True if update was successful, False otherwise
        """
        try:
            logger.debug(f"Updating image URL for madlib {filled_madlib_id}")
            result = self.collection.update_one(
                {'_id': ObjectId(filled_madlib_id)},
                {'$set': {
                    'image_url': image_url,
                    'updated_at': datetime.now(timezone.utc)
                }}
            )
            if result.matched_count == 0:
                logger.warning(f"Madlib not found: {filled_madlib_id}")
                return False

            if result.modified_count > 0:
                logger.info(f"Image URL updated for madlib: {filled_madlib_id}")
            else:
                logger.info(f"No changes made to madlib (same URL): {filled_madlib_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating image URL for madlib {filled_madlib_id}: {e}")
            return False

    def delete_filled_madlib(self, filled_madlib_id: str) -> bool:
        """
        Delete a filled madlib

        Args:
            filled_madlib_id: String representation of MongoDB ObjectId

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            logger.debug(f"Deleting filled madlib: {filled_madlib_id}")
            result = self.collection.delete_one({'_id': ObjectId(filled_madlib_id)})
            if result.deleted_count > 0:
                logger.info(f"Filled madlib deleted: {filled_madlib_id}")
            else:
                logger.info(f"Filled madlib not found: {filled_madlib_id}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting filled madlib {filled_madlib_id}: {e}")
            return False

    def get_by_id(self, filled_madlib_id: str) -> Optional[Dict]:
        """
        Retrieve a filled madlib by ID

        Args:
            filled_madlib_id: String representation of MongoDB ObjectId

        Returns:
            Dictionary containing the filled madlib or None if not found
        """
        try:
            logger.debug(f"Retrieving filled madlib by ID: {filled_madlib_id}")
            result = self.collection.find_one({'_id': ObjectId(filled_madlib_id)})
            if result:
                result['_id'] = str(result['_id'])
                result['template_id'] = str(result['template_id'])
                result['creator_id'] = str(result['creator_id'])
                logger.info(f"Filled madlib found: {filled_madlib_id}")
            else:
                logger.info(f"Filled madlib not found: {filled_madlib_id}")
            return result
        except Exception as e:
            logger.error(f"Error retrieving filled madlib {filled_madlib_id}: {e}")
            return None

    def get_by_creator(self, creator_id: str) -> List[Dict]:
        """
        Retrieve all filled madlibs created by a user

        Args:
            creator_id: String representation of MongoDB ObjectId

        Returns:
            List of filled madlibs created by the user
        """
        try:
            logger.debug(f"Retrieving filled madlibs by creator: {creator_id}")
            results = list(self.collection.find({'creator_id': ObjectId(creator_id)}))
            for result in results:
                result['_id'] = str(result['_id'])
                result['template_id'] = str(result['template_id'])
                result['creator_id'] = str(result['creator_id'])
            logger.info(f"Retrieved {len(results)} filled madlibs for creator {creator_id}")
            return results
        except Exception as e:
            logger.error(f"Error retrieving madlibs by creator {creator_id}: {e}")
            return []
        
    def get_all(self, limit: int = 100) -> List[Dict]:
        """
        Retrieve all user-filled madlibs with optional limit.

        Args:
            limit: Maximum number of filled madlibs to retrieve.

        Returns:
            List[Dict]: All filled madlibs up to the limit.
        """
        try:
            logger.debug(f"Retrieving all user-filled madlibs (limit={limit})")

            results = list(
                self.collection
                .find({})
                .sort("created_at", -1) 
                .limit(limit)
            )

            for result in results:
                if isinstance(result.get('_id'), ObjectId):
                    result['_id'] = str(result['_id'])
                if isinstance(result.get('template_id'), ObjectId):
                    result['template_id'] = str(result['template_id'])
                if isinstance(result.get('creator_id'), ObjectId):
                    result['creator_id'] = str(result['creator_id'])

            logger.info(f"Retrieved {len(results)} user-filled madlibs")
            return results

        except Exception as e:
            logger.error(f"Error retrieving user-filled madlibs: {e}")
            return []
