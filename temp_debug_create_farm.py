from webapp.services.farm_service import FarmService
from webapp.repositories.supabase_client import SupabaseClient
import traceback

client = SupabaseClient.from_env()
print('Supabase configured:', client.is_configured)
print('Supabase URL:', client.url)
print('Client class:', type(client.client))

service = FarmService()
farm_id = 'farm-test-farm'
owner_id = '11111111-1111-1111-1111-111111111111'
print('owner_id:', owner_id)
print('owner_id is None?', owner_id is None)
print('owner_id len', len(owner_id))
print('owner valid uuid?', len(owner_id) == 36)

try:
    result = service.create_farm(
        farm_id=farm_id,
        name='Test Farm',
        location='Test Location',
        farm_size='42',
        owner_id=owner_id,
    )
    print('create_farm result:', result)
except Exception as exc:
    print('EXC TYPE', type(exc).__name__)
    print('EXC', exc)
    traceback.print_exc()
