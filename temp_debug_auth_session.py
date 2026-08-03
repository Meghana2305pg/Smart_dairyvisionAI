from webapp.services.auth_service import AuthService
from webapp.repositories.supabase_client import SupabaseClient
import traceback

client = SupabaseClient.from_env()
print('Supabase configured:', client.is_configured)
print('Supabase URL:', client.url)
auth = AuthService()
email = 'debug-session-test@example.com'
password = 'Secret123!'
print('Registering', email)
try:
    user = auth.register_user(email=email, password=password)
    print('registered user', user)
    print('auth._current_user', auth._current_user)
    print('auth._session', auth._session)
    print('client.auth.get_user exists?', hasattr(auth.client.client.auth, 'get_user'))
    try:
        resp = auth.client.client.auth.get_user()
        print('get_user response', resp)
    except Exception as exc:
        print('get_user exception', type(exc).__name__, exc)
        traceback.print_exc()
    try:
        resp = auth.client.client.auth.get_session()
        print('get_session response', resp)
    except Exception as exc:
        print('get_session exception', type(exc).__name__, exc)
        traceback.print_exc()
except Exception as exc:
    print('register exception', type(exc).__name__, exc)
    traceback.print_exc()
