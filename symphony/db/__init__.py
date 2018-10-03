import os
from pymongo import ReturnDocument
from pymongo import MongoClient


class Collection:
    """Simplified version of pymongo.collection with readable methods

    :param collection: The collection that the user selects
    :type collection: pymongo.Collection
    """
    def __init__(self, collection):
        mongo_client = MongoClient(os.environ['DATABASE_URL'])
        mongo = mongo_client.db
        self.collection = mongo[collection]

    def __getitem__(self, _id):
        """Gets a document using a MongoDB ID

        :param _id: The MongoDB ID of the document to retrieve
        :type _id: str
        :returns: Document's MongoDB ID
        :rtype: pymongo.document
        """
        return self.collection.find_one({'_id': _id})

    def insert(self, document):
        """Inserts a document to the current collection and returns _id

        :param document: A document to insert into the database
        :type document: dict
        :returns: Document's MongoDB ID
        :rtype: str
        """
        _id = self.collection.insert_one(document).inserted_id
        return str(_id)

    def update(self, _id, document):
        """Updates a document and returns updated document _id

        :param _id: The MongoDB ID of the document to retrieve
        :type _id: str
        :param document: The updated document to insert into the database
        :type document: dict
        :returns: Document's MongoDB ID
        :rtype: str
        """
        document = self.collection.find_one_and_update(
            {'_id': _id},
            {'$set': document},
            return_document=ReturnDocument.AFTER
        )
        return str(document['_id'])

    def find(self, key, value):
        """Find a document with a specific key and value

        :param key: The key to search for in the document
        :param value: The value at the key to search for
        :returns: Document with corresponding key and value or None if no
            document is found
        :rtype: pymongo.Document or None
        """
        document = self.collection.find_one({key: value})
        return document
