class NewBank:
    id: int
    name: str
    city: str
    rate: float
    term: dict
    apartPrice: dict
    amountOfCredit: dict
    firstPayment: dict
    programs: list[int]




    @staticmethod
    def builderI():
        return NewBank()


# {
#     "id": 1,
#     "name": "Сбербанк",
#     "city": "Тюмень",
#     "rate": 10.5,
#     "img": "http://0.0.0.0:8080/uploads/default-thumbnail-image.jpg",
#     "term": {
#         "min": 1,
#         "max": 30
#     },
#     "apart-price": {
#         "min": 1000000,
#         "max": 2000000
#     },
#     "amount-of-credit": {
#         "min": 300000,
#         "max": 100000000
#     },
#     "first-payment": {
#         "min": 20,
#         "max": 95
#     },
#     "programs": [
#         1
#     ]
# },