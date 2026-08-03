import uuid, traceback
from webapp.services.auth_service import AuthService
from webapp.services.cow_service import CowService
from webapp.repositories.supabase_client import SupabaseClient

supaclient = SupabaseClient.from_env().client
auth = AuthService()
cow_service = CowService()

email = f"testcow+{uuid.uuid4().hex[:8]}@example.com"
password = "TestPass123!"
print('Registering user', email)
user = auth.register_user(email=email, password=password, full_name='Cow Register')
print('User id:', user.get('id'))
print('client.auth.get_session():', supaclient.auth.get_session())

try:
    print('Attempting to register cow via CowService.register_cow')
    result = cow_service.register_cow(cow_id=f'cow-{uuid.uuid4().hex[:6]}', name='Daisy')
    print('register_cow result:', result)
except Exception as e:
    print('Exception type:', type(e).__name__)
    traceback.print_exc()
    # Try to show supabase last response if available
    try:
        import sys
        print('\n--- Supabase client postgrest headers:')
        pg = getattr(supaclient, 'postgrest', None)
        if pg is not None:
            print('postgrest.headers:', pg.headers)
            print('postgrest.session.headers auth:', getattr(pg.session.headers, 'get')('Authorization'))
    except Exception as e2:
        print('failed to introspect supabase client', e2)

print('done')
