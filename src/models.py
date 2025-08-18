from dataclasses import dataclass


@dataclass(frozen=True)
class Customer:
    name: str
    age: int
    cookie: str
    banner_id: int

    @classmethod
    def header(cls) -> list[str]:
        return ["Name", "Age", "Cookie", "Banner_id"]

@dataclass
class AgeLimit:
    min_age: int = 18
    max_age: int = 100

    def is_valid(self, age: int) -> bool:
        return self.min_age <= age <= self.max_age

@dataclass(frozen=True)
class Banner:
    visitor_cookie: str
    banner_id: int

    @classmethod
    def from_customer(cls, customer: Customer) -> "Banner":
        return cls(visitor_cookie=customer.cookie, banner_id=customer.banner_id)
