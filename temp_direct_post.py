import json
from webapp.repositories.supabase_client import SupabaseClient
import httpx

client = SupabaseClient.from_env().client
pg = getattr(client, 'postgrest', None)
if pg is None:
    print('no postgrest')
    raise SystemExit(1)
base = str(pg.base_url).rstrip('/')
url = base + '/farms'
headers = {}
# gather headers from postgrest.session.headers if available
if getattr(pg, 'session', None) is not None:
    headers.update(dict(pg.session.headers))
# also include postgrest.headers mapping if present
if getattr(pg, 'headers', None) is not None:
    try:
        headers.update({k: v for k, v in pg.headers.items()})
    except Exception:
        pass

# Optionally remove the apikey header to test JWT-only auth path
if 'apikey' in headers:
    headers.pop('apikey', None)

print('POST', url)
print('headers sent:')
for k, v in headers.items():
    if k.lower() == 'authorization':
        print(k, '=>', 'Bearer ...')
    elif k.lower() == 'apikey':
        print(k, '=>', '***')
    else:
        print(k, '=>', v)

payload = {
    'id': '00000000-0000-0000-0000-000000000000',
    'farm_name': 'direct-test',
    'location': 'nowhere',
    'farm_size': 1,
}
try:
    sess = client.auth.get_session()
    user = client.auth.get_user()
    uid = None
    if user is not None:
        uid = getattr(user, 'id', None) or getattr(user, 'user_id', None)
    if uid:
        payload['owner_id'] = uid
        print('added owner_id to payload:', uid)
except Exception as e:
    print('could not read session/user', e)

with httpx.Client() as c:
    r = c.post(url, json=payload, headers=headers)
    print('status', r.status_code)
    try:
        print('body', r.json())
    except Exception:
        print('body', r.text)
