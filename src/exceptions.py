class ObjectBaseException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(ObjectBaseException):
    detail = "Object not found"

class AllRoomsAreBookedException(ObjectBaseException):
    detail = "All rooms are booked"

class NotCorrectDateException(ObjectBaseException):
    detail = "Dates not correct."


class  ObjectAlreadyExistsException(ObjectBaseException):
    detail = "Object already exists."

class HotelNotFoundException(ObjectBaseException):
    detail = "Hotel not found."

class FacilitiesNotFoundException(ObjectBaseException):
    detail = "Facilities not found."

class HotelOrRoomsNotFoundException(ObjectBaseException):
    detail = "Hotel or room not found."
