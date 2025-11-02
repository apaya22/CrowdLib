from bson import ObjectId
from typing import Optional, List, Dict
from datetime import datetime, timezone
from core.db_connect import get_collection

class MadLibTemplate:
    def __init__(self):
        self.collection = get_collection('story_templates')
        
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
            result = self.collection.find_one({'_id': ObjectId(madlib_id)})
            if result:
                result['_id'] = str(result['_id'])  # Convert ObjectId to string
            return result
        except Exception as e:
            print(f"Error retrieving madlib by ID: {e}")
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

            return results
        except Exception as e:
            print(f"Error searching madlibs by title: {e}")
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
            results = list(self.collection.find().limit(limit))

            for result in results:
                if isinstance(result.get('_id'), ObjectId):
                    result['_id'] = str(result['_id'])

            return results
        except Exception as e:
            print(f"Error retrieving all madlibs: {e}")
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
            result = self.collection.insert_one(madlib_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating madlib: {e}")
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
            result = self.collection.update_one(
                {'_id': ObjectId(madlib_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating madlib: {e}")
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
            result = self.collection.delete_one({'_id': ObjectId(madlib_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting madlib: {e}")
            return False

class UserFilledMadlibs:
    def __init__(self):
        self.collection = get_collection('filled_madlibs')

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
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating filled madlib: {e}")
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
            result = self.collection.update_one(
                {'_id': ObjectId(filled_madlib_id)},
                {'$set': {
                    'content': inputted_blanks,
                    'updated_at': datetime.now(timezone.utc)
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating filled madlib: {e}")
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
            result = self.collection.delete_one({'_id': ObjectId(filled_madlib_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting filled madlib: {e}")
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
            result = self.collection.find_one({'_id': ObjectId(filled_madlib_id)})
            if result:
                result['_id'] = str(result['_id'])
                result['template_id'] = str(result['template_id'])
                result['creator_id'] = str(result['creator_id'])
            return result
        except Exception as e:
            print(f"Error retrieving filled madlib: {e}")
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
            results = list(self.collection.find({'creator_id': ObjectId(creator_id)}))
            for result in results:
                result['_id'] = str(result['_id'])
                result['template_id'] = str(result['template_id'])
                result['creator_id'] = str(result['creator_id'])
            return results
        except Exception as e:
            print(f"Error retrieving madlibs by creator: {e}")
            return []