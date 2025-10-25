from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from backend.core.db_connect import get_collection
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MadlibTemplate:
    def __init__(self):
        self.collection = get_collection('story_templates')


    def _create_indexes(self):
        """Create indexes on frequently queried fields"""
        self.collection.create_index("name", unique=True, sparse=True)
        self.collection.create_index("_id")

    def create_template(self, name: str, title: str, template: List[Dict]) -> str:
        """
        Create a new madlib template

        Args:
            name: Unique identifier for the template (e.g., 'haunted_castle')
            title: Display title for the template
            template: Array of template segments with 'type' and other fields

        Returns:
            The MongoDB ObjectId as a string
        """
        if not name or not title or not template:
            raise ValueError("name, title, and template are required")

        template_doc = {
            "name": name,
            "title": title,
            "template": template,
            "created_at": __import__('datetime').datetime.utcnow()
        }

        try:
            result = self.collection.insert_one(template_doc)
            logger.info(f"Template created with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except DuplicateKeyError:
            logger.error(f"Template with name '{name}' already exists")
            raise ValueError(f"A template with name '{name}' already exists")

    def get_template_by_id(self, template_id: str) -> Optional[Dict]:
        """
        Retrieve a template by its MongoDB ObjectId

        Args:
            template_id: MongoDB ObjectId as a string

        Returns:
            Template document or None if not found
        """
        try:
            obj_id = ObjectId(template_id)
        except Exception:
            logger.error(f"Invalid ObjectId format: {template_id}")
            return None

        template = self.collection.find_one({"_id": obj_id})

        if template:
            template["_id"] = str(template["_id"])  # Convert ObjectId to string

        return template

    def get_template_by_name(self, name: str) -> Optional[Dict]:
        """
        Retrieve a template by its name

        Args:
            name: Template name (unique identifier)

        Returns:
            Template document or None if not found
        """
        template = self.collection.find_one({"name": name})

        if template:
            template["_id"] = str(template["_id"])

        return template

    def get_all_template_titles(self) -> List[Dict]:
        """
        Get title and ID of all templates

        Returns:
            List of dicts with 'id' and 'title' fields
        """
        templates = self.collection.find({}, {"_id": 1, "title": 1}).sort("title", 1)

        return [
            {"id": str(template["_id"]), "title": template["title"]}
            for template in templates
        ]

    def update_template(self, template_id: str, update_data: Dict) -> bool:
        """
        Update an existing template

        Args:
            template_id: MongoDB ObjectId as a string
            update_data: Dictionary of fields to update

        Returns:
            True if updated, False if not found
        """
        try:
            obj_id = ObjectId(template_id)
        except Exception:
            logger.error(f"Invalid ObjectId format: {template_id}")
            return False

        result = self.collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )

        return result.modified_count > 0

    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template by ID

        Args:
            template_id: MongoDB ObjectId as a string

        Returns:
            True if deleted, False if not found
        """
        try:
            obj_id = ObjectId(template_id)
        except Exception:
            logger.error(f"Invalid ObjectId format: {template_id}")
            return False

        result = self.collection.delete_one({"_id": obj_id})
        return result.deleted_count > 0

