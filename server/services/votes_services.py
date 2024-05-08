from data.models.vote import VoteStatus
from data.database import insert_query, read_query, update_query


def get_all(reply_id: int, type: str):
    data = read_query('''SELECT count(type) FROM votes
                      WHERE reply_id=?
                      AND type=?''',
                      (reply_id, VoteStatus.str_to_int[type]))
    if data:
        return data[0][0]


def get_vote_with_type(reply_id: int, user_id: int):
    vote_type = read_query('SELECT type FROM votes WHERE reply_id=? AND user_id=?',
                           (reply_id, user_id))

    if vote_type:
        return VoteStatus.int_to_str[vote_type[0][0]]


def add_vote(user_id, reply_id: int, type: str):
    insert_query('INSERT INTO votes(user_id, reply_id, type) VALUES(?,?,?)',
                 (user_id, reply_id, VoteStatus.str_to_int[type]))


def switch_vote(user_id, reply_id: int, type: str):
    new_type = 'up' if type == 'down' else 'down'
    update_query('UPDATE votes SET type = ? WHERE user_id = ? AND reply_id = ?',
                 (VoteStatus.str_to_int[new_type], user_id, reply_id))


def delete_vote(reply_id: int, user_id: int):
    update_query('''DELETE FROM votes
                  WHERE reply_id = ? AND user_id = ?''', (reply_id, user_id))
