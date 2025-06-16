import reflex as rx

class User(rx.Model, table=True):
    username: str = rx.Field(unique=True, index=True)
    hashed_password: str
    email: str = rx.Field(default="")
    is_active: bool = rx.Field(default=True)

    def __str__(self):
        return self.username
