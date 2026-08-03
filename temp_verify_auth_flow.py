import uuid
from webapp.services.auth_service import AuthService
from webapp.services.farm_service import FarmService
from webapp.repositories.supabase_client import SupabaseClient

# Create services
supaclient = SupabaseClient.from_env().client
auth = AuthService()
farm_service = FarmService()

# Register a temporary user
email = f"test+{uuid.uuid4().hex[:8]}@example.com"
password = "TestPass123!"
print('registering', email)
user = auth.register_user(email=email, password=password, full_name='Tmp User')
print('registered user id:', user.get('id'))

# Check auth session and headers
try:
    sess = supaclient.auth.get_session()
    print('client.auth.get_session():', sess)
except Exception as e:
    print('get_session exception', e)

# Inspect postgrest headers
pg = getattr(supaclient, 'postgrest', None)
if pg is not None:
    hdrs = getattr(pg, 'headers', None)
    print('postgrest.headers:', hdrs)
    sess_client = getattr(pg, 'session', None)
    if sess_client is not None:
        try:
            print('postgrest.session.headers[authorization]:', sess_client.headers.get('Authorization'))
        except Exception as e:
            print('session.headers inspect error', e)

# Create a farm as this user
owner_id = user.get('id')
try:
    farm_id = f'farm-{uuid.uuid4().hex[:6]}'
    result = farm_service.create_farm(farm_id=farm_id, name='Temp Farm', location='Test Location', farm_size='10', owner_id=owner_id)
    print('create_farm result:', result)
except Exception as e:
    print('create_farm exception:', type(e).__name__, e)

# Query farms table for owner
try:
    resp = supaclient.table('farms').select('*').eq('owner_id', owner_id).execute()
    print('supabase farms query error:', getattr(resp, 'error', None))
    print('supabase farms data count:', len(getattr(resp, 'data', []) or []))
    print('sample data:', getattr(resp, 'data', []) )
except Exception as e:
    print('query exception', e)

# Logout
auth.logout()
print('logged out')
# Check headers cleared
if pg is not None:
    try:
        print('postgrest.session.headers after logout:', pg.session.headers.get('Authorization'))
    except Exception as e:
        print('postgrest.session.headers inspect error', e)

print('done')
