from typing import Optional
from db import get_nodes_of_label, get_db
from llama_index.core.graph_stores.types import LabelledNode

# HELPER FUNCTIONS
def find_max_id(label: str, unique_key: str) -> int:
    nodes = get_nodes_of_label(label)
    max_id = 0
    for node in nodes:
        max_id = max(max_id, node[unique_key])
    return max_id

# CREATE METHODS
def create_user(username: str) -> int:
    db = get_db()
    query = "CREATE (u:User {user_id: $user_id, username: $username}) RETURN u"
    user_id = find_max_id('User', 'user_id') + 1
    user = db.structured_query(query, param_map={"user_id": user_id, "username": username})[0]
    return user['u']['user_id']

def create_conversation(user_id: int) -> int:
    db = get_db()
    if user_id == -1:
        user_id = create_user("anon")
    query = "MATCH (u:User) WHERE u.user_id = $user_id CREATE (u)-[:PARTICIPANT]->(c:Conversation {conversation_id: $conversation_id}) RETURN c"
    conversation_id = find_max_id('Conversation', 'conversation_id') + 1
    return db.structured_query(query, param_map={"user_id": user_id, "conversation_id": conversation_id})[0]['c']['conversation_id']

def create_message(conversation_id: int, message: str, sent_by_user: bool = True):
    db = get_db()
    if conversation_id == -1:
        conversation_id = create_conversation(-1)
    message_id = find_max_id('Message', 'message_id') + 1
    query = "MATCH (c:Conversation) WHERE c.conversation_id = $conversation_id CREATE (c)-[:HAS_MSG]->(m:Message {message_id: $message_id, message: $message, sent_by_user: $sent_by_user}) RETURN m"
    return db.structured_query(query, param_map={"message_id": message_id, "conversation_id": conversation_id, "message": message, "sent_by_user": sent_by_user})

# GET METHODS
def get_user(user_id: int) -> Optional[LabelledNode]:
    db = get_db()
    query = "MATCH (u:User) WHERE u.user_id = $user_id RETURN u"
    users = db.structured_query(query, param_map={"user_id": user_id})
    if len(users) == 0:
        return None
    return users[0]['u']

def get_conversations(user_id: int) -> list[LabelledNode]:
    db = get_db()
    user = get_user(user_id)
    if not user:
        return []
    query = "MATCH (u:User)-[:PARTICIPANT]->(c:Conversation) WHERE u.user_id = $user_id RETURN c"
    return db.structured_query(query, param_map={"user_id": user['user_id']})

def get_messages(conversation_id: int) -> list[LabelledNode]:
    db = get_db()
    query = "MATCH (c:Conversation) WHERE c.conversation_id = $conversation_id RETURN c"
    conversation = db.structured_query(query, param_map={"conversation_id": conversation_id})
    if len(conversation) == 0:
        return []
    query = "MATCH (c:Conversation)-[:HAS_MSG]->(m:Message) WHERE c.conversation_id = $conversation_id RETURN m ORDER BY m.message_id"
    return db.structured_query(query, param_map={"conversation_id": conversation_id})


if __name__ == "__main__":
    print(get_messages(2))
