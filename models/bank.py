from pydantic import BaseModel, Field


class Term(BaseModel):
    min: int
    max: int


class Price(BaseModel):
    min: int
    max: int


class Payment(BaseModel):
    min: int
    max: int


class Program(BaseModel):
    text: str
    id: int = Field(alias="value")


class AmountCredit(BaseModel):
    min: int
    max: int


class City(BaseModel):
    id: int = Field(alias="val")
    text: str
    code: str


class Bank(BaseModel):
    id: int
    name: str
    city: City = None
    rate: float
    img: str
    term: Term
    apart_price: Price = Field(alias="apart-price")
    amount_of_credit: AmountCredit = Field(alias="amount-of-credit")
    firstPayment: Payment = Field(alias="first-payment")
    program: list[Program] = None
