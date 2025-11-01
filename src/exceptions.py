class ObjectBaseException(Exception):
    default_detail = "Неожиданная ошибка"

    def __init__(self, detail: str | None = None, *args, **kwargs):
        self.detail = detail or self.default_detail
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(ObjectBaseException):
    default_detail = "Object not found."


class AllRoomsAreBookedException(ObjectBaseException):
    default_detail = "All rooms are booked."


class NotCorrectDateException(ObjectBaseException):
    default_detail = "Dates not correct."


class ObjectAlreadyExistsException(ObjectBaseException):
    default_detail = "Object already exists."


class HotelNotFoundException(ObjectBaseException):
    default_detail = "Hotel not found."


class FacilitiesNotFoundException(ObjectBaseException):
    default_detail = "Facilities not found."


class HotelOrRoomsNotFoundException(ObjectBaseException):
    default_detail = "Hotel or room not found."
