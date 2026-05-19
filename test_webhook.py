import urllib.request, json

req = urllib.request.Request(
    'https://partou.app.n8n.cloud/webhook/03a8a398-4616-4dad-9e1d-e94c9303d529',
    headers={'Authorization': 'Iu8pe15v_YRl'}
)
with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read().decode())

if isinstance(data, list):
    print(f'OK - Array met {len(data)} items')
    if data:
        print('Velden:', list(data[0].keys()))
        print('Eerste item:', json.dumps(data[0], indent=2, ensure_ascii=False))
elif isinstance(data, dict):
    print('Dict met velden:', list(data.keys()))
    if 'items' in data:
        print(f'items-veld bevat {len(data["items"])} records')
        print('Eerste item:', json.dumps(data['items'][0], indent=2, ensure_ascii=False))
