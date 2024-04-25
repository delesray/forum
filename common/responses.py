from fastapi import Response


class BadRequest(Response):
    def __init__(self, content=''):
        super().__init__(status_code=400, content=content)


class NotFound(Response):
    def __init__(self, content=''):
        super().__init__(status_code=404, content='No such resource')


class Unauthorized(Response):
    def __init__(self, content=''):
        super().__init__(status_code=401, content=content)


class Forbidden(Response):

    def __init__(self, content=''):
        super().__init__(status_code=403, content="You must be admin!")


class NoContent(Response):
    def __init__(self):
        super().__init__(status_code=204)


class Created(Response):
    def __init__(self):
        super().__init__(status_code=201)


class InternalServerError(Response):
    def __init__(self):
        super().__init__(status_code=500)
