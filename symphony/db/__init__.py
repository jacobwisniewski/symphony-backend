"""
Class collection simplifies pymongo.collection to its main functions
"""
import os
from pymongo import ReturnDocument
from pymongo import MongoClient


class Collection:
    def __init__(self, collection):
        mongo_client = MongoClient(os.environ['DATABASE_URL'])
        mongo = mongo_client.db
        self.collection = mongo[collection]

    def __getitem__(self, _id):
        """Gets a document using a MongoDB ID"""
        return self.collection.find_one({'_id': _id})

    def insert(self, document):
        """Inserts a document to the current collection and returns _id"""
        _id = self.collection.insert_one(document).inserted_id
        return str(_id)

    def update(self, _id, document):
        """Updates a document and returns updated document"""
        document = self.collection.find_one_and_update(
            {'_id': _id},
            {'$set': document},
            return_document=ReturnDocument.AFTER
        )
        return document['_id']

    def find(self, key, value):
        """Find a document with a specific key and value"""
        document = self.collection.find_one({key: value})
        return document
