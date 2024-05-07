from data.models.vote import VoteStatus
from data.database import insert_query, read_query, update_query


def get_all(reply_id: int, type: str):
    data = read_query('''SELECT count(type) FROM votes
                      WHERE reply_id=?
                      AND type=?''', 
                      (reply_id, VoteStatus.str_to_int[type]))
    if data:
        return data[0][0]


def vote_exists(reply_id: int, user_id: int):
    return any(read_query('SELECT 1 FROM votes WHERE reply_id=? AND user_id=?', 
                      (reply_id, user_id)))


def add_vote(user_id, reply_id: int, type: str):
    insert_query('INSERT INTO votes(user_id, reply_id, type) VALUES(?,?,?)', 
                 (user_id, reply_id, VoteStatus.str_to_int[type]))


def switch_vote(user_id, reply_id: int, type: str):
    update_query('UPDATE votes SET type = ? WHERE user_id = ? AND reply_id = ?',
                 (VoteStatus.str_to_int[type], user_id, reply_id))


def delete_vote(reply_id: int, user_id: int):
    update_query('''DELETE FROM votes
                  WHERE reply_id = ? AND user_id = ?''', (reply_id, user_id))
