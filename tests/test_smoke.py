import sys, os
from urllib.parse import urlencode

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from app import app
except Exception as e:
    print(f"IMPORT_ERR {e}")
    sys.exit(1)


def check(endpoint: str):
    with app.test_client() as c:
        rv = c.get(endpoint)
        print(endpoint, rv.status_code)
        if rv.status_code != 200:
            return False
        return True


def main():
    ok = True
    endpoints = [
        '/',
        '/search',
        '/trends',
        '/about',
    ]
    for ep in endpoints:
        ok = check(ep) and ok

    # results with query params
    params = {
        'origin': 'SYD',
        'destination': 'MEL',
        'date_from': '2025-09-01',
        'date_to': '2025-09-07',
    }
    ok = check('/results?' + urlencode(params)) and ok

    print('SMOKE_OK' if ok else 'SMOKE_FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

