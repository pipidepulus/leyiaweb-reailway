import reflex as rx
import reflex_local_auth
import sqlmodel

class UserInfo(rx.Model, table=True):
    email: str
    user_id: int = sqlmodel.Field(foreign_key="localuser.id")
    created_from_ip: str = ""

class MyRegisterState(reflex_local_auth.RegistrationState):
    def handle_registration_email(self, form_data):
        registration_result = self.handle_registration(form_data)
        if self.new_user_id >= 0:
            with rx.session() as session:
                session.add(
                    UserInfo(
                        email=form_data["email"],
                        created_from_ip=self.router.headers.get(
                            "x_forwarded_for", self.router.session.client_ip
                        ),
                        user_id=self.new_user_id,
                    )
                )
                session.commit()
        return registration_result
