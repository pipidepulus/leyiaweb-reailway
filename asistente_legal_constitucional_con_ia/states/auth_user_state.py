import reflex as rx
import reflex_local_auth
import sqlmodel
from asistente_legal_constitucional_con_ia.states.register_state import UserInfo
from typing import Optional

class MyLocalAuthState(reflex_local_auth.LocalAuthState):
    @rx.var(cache=True)
    def authenticated_user_info(self) -> Optional[UserInfo]:
        if self.authenticated_user.id < 0:
            return
        with rx.session() as session:
            return session.exec(
                sqlmodel.select(UserInfo).where(
                    UserInfo.user_id == self.authenticated_user.id
                ),
            ).one_or_none()
