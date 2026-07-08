import app

print('Routes:')
for rule in app.app.url_map.iter_rules():
    print(rule.rule)

client = app.app.test_client()
resp = client.get('/')
print('GET / ->', resp.status_code)
print('Content-Type ->', resp.headers.get('Content-Type'))
