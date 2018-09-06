"""
Class collection simplifies pymongo.collection to its main functions
"""
from app import db
from pymongo import ReturnDocument


class Collection:
    def __init__(self, collection):
        self.collection = db[collection]

    def __getitem__(self, _id):
        """Gets a document using _id"""
        return self.collection.find_one({'_id': _id})

    def insert(self, document):
        """Inserts a document to the current collection and returns _id"""
        _id = self.collection.insert_one(document).inserted_id
        return str(_id)

    def update(self, _id, document):
        """Updates a document and returns updated document"""
        document = self.collection.find_one_and_update(
            {'_id': _id, '$set': document},
            return_document=ReturnDocument.AFTER
        )
        return document

    def find(self, key, value):
        """Find a document with a specific key and value"""
        document = self.collection.find_one({key: value})
        return document
