from webapp.repositories.supabase_client import SupabaseClient
c = SupabaseClient.from_env().client
print(type(c))
print([a for a in dir(c) if 'option' in a.lower() or 'headers' in a.lower() or 'postg' in a.lower()][:400])
opts = getattr(c, 'options', None)
print('opts', opts)
print('opts.headers', getattr(opts, 'headers', None))
print('\npostgrest obj:', getattr(c, 'postgrest', None))
pg = getattr(c, 'postgrest', None)
if pg is not None:
    print('pg.headers', getattr(pg, 'headers', None))
    print('pg.session', getattr(pg, 'session', None))
    print('pg.base_url', getattr(pg, 'base_url', None))
    try:
        print('pg._client', getattr(pg, '_client', None))
    except Exception as e:
        print('pg._client except', e)
