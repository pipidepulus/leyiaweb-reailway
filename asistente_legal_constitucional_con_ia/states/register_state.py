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
                client_ip_str = "unknown"
                try:
                    # Tratar de obtener x-forwarded-for primero
                    x_forwarded_for = self.router.headers.x_forwarded_for
                    if x_forwarded_for:
                        # Puede ser una cadena separada por comas o una lista
                        if isinstance(x_forwarded_for, list):
                            client_ip_str = x_forwarded_for[0]
                        else:
                            client_ip_str = x_forwarded_for.split(',')[0]
                    else:
                        # Fallback a client_ip si x-forwarded-for no está o está vacío
                        client_ip_str = self.router.session.client_ip
                except AttributeError:
                    # Fallback si x_forwarded_for no es un atributo directo
                    try:
                        client_ip_str = self.router.session.client_ip
                    except AttributeError:
                        pass # Dejar como unknown si ninguno está disponible
                
                session.add(
                    UserInfo(
                        email=form_data["email"],
                        created_from_ip=client_ip_str.strip() if client_ip_str else "unknown",
                        user_id=self.new_user_id,
                    )
                )
                session.commit()
        return registration_result
