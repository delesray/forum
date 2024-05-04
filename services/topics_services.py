from __future__ import annotations
from data.models.topic import Status, TopicResponse, TopicCreate, PaginationInfo, Links, TopicWithReplies
from data.models.user import User
from data.database import read_query, update_query, insert_query
from mariadb import IntegrityError
from fastapi import HTTPException
from common.responses import NotFound, Forbidden
from math import ceil
from starlette.requests import  Request
from urllib.parse import parse_qs, quote
from data.models.reply import ReplyResponse




_TOPIC_BEST_REPLY = None


def get_all(
        page: int,
        size: int,
        search: str = None,
        username: str = None,
        category: str = None,
        status: str = None,
        sort: str = None,
        sort_by: str = None
):
    query_params = ()
    sql = '''SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id, t.category_id, c.name
             FROM topics t 
             JOIN users u ON t.user_id = u.user_id
             JOIN categories c ON t.category_id = c.category_id'''

    if search:
        sql += ' AND title LIKE ?'
        query_params += (f'%{search}%',)

    if username:
        if username not in get_usernames():
            raise HTTPException(status_code=400, detail="Invalid username")

        sql += ' AND u.username = ?'
        query_params += (username,)

    if category:
        if category not in get_categories_names():
            raise HTTPException(status_code=400, detail="Invalid category")

        sql += ' AND c.name = ? '
        query_params += (category,)

    if status:
        if status not in [Status.OPEN, Status.LOCKED]:
            raise HTTPException(status_code=400, detail="Invalid status value")

        sql += ' AND t.is_locked = ? '
        query_params += (Status.str_int[status],)
        
        
    if sort and (sort.lower() in ('asc', 'desc')):
        sql += f' ORDER BY {sort_by} {sort}'

    pagination = pagination_info(sql, query_params, page, size)

    pagination_sql = sql + ' LIMIT ? OFFSET ?'
    query_params += (size, size * (page - 1))

    data = read_query(pagination_sql, query_params)

    topics = [TopicResponse.from_query(*row) for row in data]
    return topics, pagination


def get_by_id(topic_id: int):
    data = read_query(
        '''SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id, t.category_id, c.name
               FROM topics t 
               JOIN users u ON t.user_id = u.user_id
               JOIN categories c ON t.category_id = c.category_id WHERE t.topic_id = ?''', (topic_id,))

    return next((TopicResponse.from_query(*row) for row in data), None)


# def get_by_id_cat_id(topic_id: int) -> Topic | None:  # Miray
#     data = read_query(
#         '''SELECT topic_id, title, user_id, is_locked, best_reply_id, category_id 
#         FROM topics WHERE topic_id = ?''', (topic_id,))

#     return next((Topic.from_query(*row) for row in data), None)


def create(topic: TopicCreate, customer: User):
    try:
        generated_id = insert_query(
            'INSERT INTO topics(title, user_id, is_locked, best_reply_id, category_id) VALUES(?,?,?,?,?)',
            (topic.title, customer.user_id, Status.str_int["open"], _TOPIC_BEST_REPLY, topic.category_id))

        return generated_id
        # return TopicResponse(
        # )

    except IntegrityError as e:
        return e


def update_title(topic_id, title):
    update_query(
        '''UPDATE topics SET
           title = ?
           WHERE topic_id = ? 
        ''',
        (title, topic_id))

    return f"Project title updated to {title}"


def update_best_reply(topic_id, best_reply_id):
    update_query(
        '''UPDATE topics SET
           best_reply_id = ?
           WHERE topic_id = ? 
        ''',
        (best_reply_id, topic_id))

    return f"Project Best Reply Id updated to {best_reply_id}"


def custom_sort(topics: list[TopicResponse], attribute, reverse=False):
    return sorted(
        topics,
        key=lambda t: getattr(t, attribute) if getattr(t, attribute) is not None else float('inf'),
        # float('inf') - positive infinity, None values are treated as if are greater than any real val
        reverse=reverse)


def get_topic_replies(topic_id: int) -> list[int]:
    data = read_query(
        '''SELECT reply_id
        FROM replies WHERE topic_id = ?''', (topic_id,))

    replies_ids = [tupl[0] for tupl in data]
    return replies_ids


def get_categories_names():
    data = read_query(
        '''SELECT name FROM categories''')

    categories_names = [tupl[0] for tupl in data]

    return categories_names


def get_usernames():
    data = read_query(
        '''SELECT username FROM users''')

    usernames = [tupl[0] for tupl in data]
    return usernames


# def get_category_by_name(category_name: str) -> Category:
#     data = read_query(
#         '''SELECT category_id, name, is_locked, is_private
#         FROM categories WHERE name = ?''', (category_name,))

#     return next((Category.from_query(*row) for row in data), None)


# def topic_with_replies(topic: TopicResponse):
#     replies = get_all_replies(topic.topic_id)

#     topic_with_replies = {
#         "topic": topic,
#         "replies": replies if replies else []
#     }

#     return topic_with_replies


# def get_topics_from_private_categories(current_user: User) -> list[TopicResponse]:
#     data = read_query(
#         '''SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id, t.category_id, c.name
#            FROM topics t 
#            JOIN users u ON t.user_id = u.user_id
#            JOIN categories c ON t.category_id = c.category_id
#            JOIN users_categories_permissions ucp ON c.category_id = ucp.category_id
#            WHERE c.is_private = ?
#            AND ucp.user_id = ?''', (1, current_user.user_id))

#     topics = [TopicResponse.from_query(*row) for row in data]
#     return topics


def validate_topic_access(topic_id: int, user: User):
    existing_topic = get_by_id(topic_id)

    if not existing_topic:
        return NotFound(f"Topic #ID:{topic_id} does not exist")

    if existing_topic.status == Status.LOCKED:
        return Forbidden(f"Topic #ID:{existing_topic.topic_id} is locked")

    if existing_topic.user_id != user.user_id:
        return Forbidden('You are not allowed to edit topics created by other users')

    return None


def exists(id: int):
    return any(read_query('SELECT 1 from topics WHERE topic_id=?', (id,)))


from services.replies_services import get_all as get_all_replies


def update_locking(locking: bool, topic_id: int):
    update_query('UPDATE topics SET is_locked = ? WHERE topic_id = ?',
                 (locking, topic_id))


def is_owner(topic_id: int, user_id: int):
    data = read_query('SELECT FROM topics = ? WHERE topic_id = ? AND user_id = ?',
                      (topic_id, topic_id))
    if not data:
        return False
    return True


def pagination_info(sql, query_params, page, size):
    count_sql = f'SELECT COUNT(*) FROM ({sql}) as filtered_topics'
    # todo discuss
    data = read_query(count_sql, query_params)
    total = data[0][0]

    if not total:
        return None
    else:
        return PaginationInfo(
            total_topics=total,
            page=page,
            size=size,
            pages=ceil(total / size)
        )


def create_links(request: Request, page: int, size: int, total: int):
    # base_url = str(request.url_for("get_all_topics"))

    last_page = ceil(total / size) if total > 0 else 1

    links = Links(
        self=f"{request.url}",
        first=f"{result_url(request, 1, size)}",
        last=f"{result_url(request, last_page, size)}",
        next=f"{result_url(request, page + 1, size)}" if page * size < total else None,
        prev=f"{result_url(request, page - 1, size)}" if page - 1 >= 1 else None
    )
    return links


def result_url(request: Request, page: int, size: int):
    parsed_query = parse_qs(request.url.query)
  
    parsed_query.update({'page': [str(page)], 'size': [str(size)]})
    new_query = '&'.join(f'{key}={quote(val[0])}' for key, val in parsed_query.items())
    
    new_url = f'{request.url.scheme}://{request.url.netloc}{request.url.path}'
    if new_query:
        new_url += f'?{new_query}'

    return new_url


def dto(data):
    replies = []

    for tid, t_title, tuserid, u_username, tislocked, tbrid, tcategoryid, cname, r_replyid, rtext, r_username  in data:
        if any(data[0][8:]):  
            replies.append(
                ReplyResponse.from_query(*(r_replyid, rtext, r_username, tid))
            )
            
    topic = TopicResponse.from_query(tid, t_title, tuserid, u_username, tislocked, tbrid, tcategoryid, cname)

    topic_with_replies = TopicWithReplies.from_query(topic, replies)
    return topic_with_replies


def get_topic_by_id_with_replies(topic_id: int):
    data = read_query(
        '''SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id,
           t.category_id, c.name, r.reply_id, r.text, ur.username 
           FROM topics t 
           JOIN users u ON t.user_id = u.user_id
           JOIN categories c ON t.category_id = c.category_id
           LEFT JOIN replies r ON t.topic_id = r.topic_id
           LEFT JOIN users ur ON r.user_id = ur.user_id
           WHERE t.topic_id = ?''', (topic_id,))
    
    if not data:
        return None

    topic_dto = dto(data)
    return topic_dto

    
   
