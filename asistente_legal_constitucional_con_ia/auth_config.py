# asistente_legal_constitucional_con_ia/auth_config.py
"""Configuración de autenticación local."""

from reflex_local_auth import LocalAuthConfig

# Configuración de autenticación
auth_config = LocalAuthConfig(
    # Configuración de sesiones
    session_cookie_name="legal_assistant_session",
    session_expiry_delta=86400 * 7,  # 7 días
    
    # Configuración de registro/login
    require_email_confirmation=False,  # Simplificar para desarrollo
    allow_registration=True,
    
    # Configuración de URL
    login_route="/login",
    register_route="/register",
    logout_route="/logout",
    protected_route_redirect="/login",
)
