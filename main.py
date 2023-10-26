from datetime import datetime
from typing import List, Optional
import psycopg2
from flask import Flask, request, jsonify

DATABASE_CONFIG = {
    "host": "192.168.1.172",
    "database": "sdpx_db",
    "user": "postgres",
    "password": "12345"
}

class Database:
    def __init__(self, config):
        self.connection = psycopg2.connect(**config)
        self.cursor = self.connection.cursor()

    def execute(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor

    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

class User:
    def __init__(self, user_id: int = None, name: str = None , db: Database = None):
        self.user_id = user_id
        self.name = name
        self.friends: List["User"] = []
        self.db = Database(DATABASE_CONFIG)
    def view_posts(self,friendlist) -> List["Post"]:
        cur.execute("SELECT * FROM posts WHERE user_id = {self.user_id} AND friend_id IN {friendlist}")
        rows = cur.fetchall()
        pass
    
    def view_all_posts(self) -> List["Post"]:
        rows = self.db.execute("SELECT * FROM post")
        columns = [desc[0] for desc in rows.description]
        rows = rows.fetchall()
        rows = [dict(zip(columns, row)) for row in rows]
        return rows

    def view_user_posts(self) -> List["Post"]:
        rows = self.db.execute("SELECT * FROM post WHERE user_id = (%s)" , [self.user_id])
        columns = [desc[0] for desc in rows.description]
        rows = rows.fetchall()
        rows = [dict(zip(columns, row)) for row in rows]
        return rows

    def view_location_posts(self, location: "Location") -> List["Post"]:
        rows =self.db.execute("SELECT * FROM post WHERE location_id = (%s)" , [location])
        columns = [desc[0] for desc in rows.description]
        rows = rows.fetchall()
        rows = [dict(zip(columns, row)) for row in rows]
        return rows

    def get_friends(self) -> List["User"]:
        cur.execute("SELECT friend_id FROM friends WHERE user_id = {self.user_id}")
        rows = cur.fetchall()
        return rows
    def get_user_id(self):
        return self.user_id

class Post:
    def __init__(self, post_id: int, content: str, timestamp: datetime, user_id: int, db: Database):
        self.user_id = user_id
        self.post_id = post_id
        self.content = content
        self.timestamp = timestamp
        self.tagged_friends: List[User] = []
        self.location: Optional[Location] = None
        self.db = db

    def create(self):
        #create post id
        quary = "insert into public.post"
        try:
            if self.location is not None:
                quary += "(post_id, content, timestamp, user_id, location_id) VALUES (%s,%s,%s,%s,%s)"
                self.db.execute(quary, (self.post_id, self.content, self.timestamp, self.user_id, self.location))
                self.db.commit()
                self.db.close()
            if self.tagged_friends is not None:
                for friend in self.tagged_friends:
                    cur.execute("INSERT INTO tagged_friends (post_id,friend_id) VALUES (%s,%s)" ,(self.post_id,friend.user_id))
                    conn.commit()
            return {"status": "success"}
        except Exception as e:
            print(e)
            return {"status": "failed"}

    def tag_location(self, location_id: None):
        self.location = location_id

    def tag_friend(self, friend: None):
        self.tagged_friends = friend

   


# class TaggedFriend:
#     def __init__(self, timestamp: datetime):
#         self.timestamp = timestamp


class Location:
    def __init__(self, location_id: int):
        self.location_id = location_id
    def get_location(self):
        try:
            cur.execute("SELECT * FROM location WHERE location_id = (%s) ",{self.location_id})
            rows = cur.fetchone()
            return rows
        except Exception as e:
            return None


app = Flask(__name__)
db = Database(DATABASE_CONFIG)

@app.route('/create_post', methods=['POST' , 'GET'])
def create_post():
    try:
        json = request.get_json()
        content = json['content']
        user_id = json['user_id']
        location_tag = json['location_tag']
        friend_tag = json['friend_tag'] if 'friend_tag' in json else None
      
    except Exception as e:
        print(e)
    check = db.execute("SELECT post_id FROM post ORDER BY post_id DESC")
    check = check.fetchone()
    check = check[0]
    if check is None:
        post_id = 1
    else:
        print(check)
        post_id = check + 1
    user = User(user_id, 'Test User')
    print(friend_tag)
    post = Post(post_id, content, datetime.now(),user.get_user_id(),db)
    post.tag_location(location_tag)
    post.tag_friend(friend_tag)
    result = post.create()
    return jsonify(result)

@app.route('/view_all_post', methods=['GET'])
def view_posts():
    try:
        user = User(db=db)
        posts = user.view_all_posts()
        return jsonify(posts)
    except Exception as e:
        print(e)
        return jsonify({"status": "failed"})

@app.route('/view/user/<int:user_id>', methods=['GET'])
def view_user_posts(user_id):
    try:
        user = User(user_id, db=db)
        posts = user.view_user_posts()
        return jsonify(posts)
    except Exception as e:
        print(e)
        return jsonify({"status": "failed"})

@app.route('/view/location/<int:location_id>', methods=['GET'])
def view_location_posts(location_id):
    try:
        user = User(db=db)
        posts = user.view_location_posts(location_id)
        return jsonify(posts)
    except Exception as e:
        print(e)
        return jsonify({"status": "failed"})





if __name__ == '__main__':
    app.run(port=5050, debug=True)