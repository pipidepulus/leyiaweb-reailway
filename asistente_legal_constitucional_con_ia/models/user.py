# from sqlmodel import Field  # Import Field from sqlmodel
# import reflex as rx


# class LocalUser(rx.Model, table=True):
#     username: str = Field(unique=True, index=True)  # Use sqlmodel.Field
#     password_hash: str
#     email: str = Field(default="")  # Use sqlmodel.Field
#     enabled: bool = Field(default=True)  # Use sqlmodel.Field

#     def __str__(self):
#         return self.username
