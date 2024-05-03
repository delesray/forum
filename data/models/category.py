from pydantic import BaseModel


class Category(BaseModel):
    category_id: int | None = None
    name: str
    is_locked: bool = False
    is_private: bool = False

    @classmethod
    def from_query(cls, category_id, name, is_locked, is_private):
        return cls(
            category_id=category_id,
            name=name,
            is_locked=True if is_locked == 1 else False,
            is_private=True if is_private == 1 else False
        )


class CategoryWithTopics(BaseModel):
    category_id: int | None = None
    name: str
    is_locked: bool = False
    is_private: bool = False
    topics: list | str | None = None

    @classmethod
    def from_query(cls, category_id, name, is_locked, is_private, topics=None):
        return cls(
            category_id=category_id,
            name=name,
            is_locked=True if is_locked == 1 else False,
            is_private=True if is_private == 1 else False,
            topics=topics if topics else 'No topics')
