from webapp.repositories.supabase_client import SupabaseClient

c = SupabaseClient.from_env().client
print('client type:', type(c))

print('\n-- auth --')
print('has set_session:', hasattr(c.auth,'set_session'))
print('has get_user:', hasattr(c.auth,'get_user'))
print('auth session attr:', getattr(c.auth, 'session', None))
try:
    print('auth dir sample:', [a for a in dir(c.auth) if 'session' in a.lower() or 'token' in a.lower()][:40])
except Exception as e:
    print('auth dir failed', e)

print('\n-- postgrest / headers --')
print('has postgrest:', hasattr(c, 'postgrest'))
if hasattr(c, 'postgrest'):
    pr = c.postgrest
    print('postgrest type:', type(pr))
    try:
        print('postgrest dir sample:', dir(pr)[:60])
    except Exception as e:
        print('postgrest dir failed', e)
    # Try common internal fields
    for candidate in ('_client','client','session','headers','http'):
        obj = getattr(pr, candidate, None)
        if obj is not None:
            print(f'postgrest.{candidate} ->', type(obj))
            try:
                print(repr(obj)[:400])
            except Exception:
                pass

# Try to inspect request headers used by postgrest client if possible
print('\n-- try to find headers in nested objects --')
checked = set()
def walk(obj, depth=0):
    if depth>3 or id(obj) in checked:
        return
    checked.add(id(obj))
    for name in dir(obj):
        if name.startswith('_'):
            continue
        try:
            attr = getattr(obj, name)
        except Exception:
            continue
        t = type(attr)
        if 'headers' in name.lower():
            print('found headers attr at', obj, name, getattr(attr, '__dict__', repr(attr)[:200]))
        if depth<2 and (not isinstance(attr, (str, int, float, bytes))):
            try:
                walk(attr, depth+1)
            except Exception:
                pass

try:
    walk(c)
except Exception as e:
    print('walk failed', e)

print('\n-- auth.get_user()/get_session output --')
try:
    gu = c.auth.get_user()
    print('get_user:', gu)
except Exception as e:
    print('get_user exception', e)
try:
    gs = c.auth.get_session()
    print('get_session:', gs)
except Exception as e:
    print('get_session exception', e)

print('\n-- done --')
