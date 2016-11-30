import pymongo


class User:
    def __init__(self, client_id):
        self.user_id = client_id.split('.')[0]
        self.visited = []
        self._load()

    def _load(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client.housefinder
        db_user = db.users.find_one({'user_id': self.user_id})
        if db_user:
            # load user
            self.visited = db_user['visited']
        else:
            # create new user
            db.users.insert_one({'user_id': self.user_id, 'visited': []})
            self._load()
