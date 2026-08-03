import uuid
from webapp.services.auth_service import AuthService
from webapp.services.farm_service import FarmService
from webapp.repositories.supabase_client import SupabaseClient
import traceback

client = SupabaseClient.from_env()
print('Supabase configured:', client.is_configured)
print('Supabase URL:', client.url)

auth = AuthService()
email = f"debug+{uuid.uuid4()}@example.com"
password = 'Secret123!'
print('Registering user', email)
try:
    user = auth.register_user(email=email, password=password)
    print('registered user', user)
except Exception as exc:
    print('registration failed', type(exc).__name__, exc)
    traceback.print_exc()
    raise

print('Current user after register', auth.current_user())
service = FarmService()
farm_id = 'farm-test-farm'
owner_id = auth.current_user().get('id') if auth.current_user() else None
print('owner_id', owner_id)
try:
    result = service.create_farm(
        farm_id=farm_id,
        name='Test Farm',
        location='Test Location',
        farm_size='42',
        owner_id=owner_id,
    )
    print('create_farm result', result)
except Exception as exc:
    print('create_farm failed', type(exc).__name__, exc)
    traceback.print_exc()
