from app import app

def test_routes():
    client = app.test_client()

    # 1. Test Index
    r1 = client.get('/')
    assert r1.status_code == 200, f'Index failed: {r1.status_code}'
    assert b'MINE' in r1.data
    assert b'Fleet Controller' in r1.data
    print('GET / -> OK (200)')

    # 2. Test Truck Views
    for tid in ['Truck A', 'Truck B', 'Truck C', 'Truck D']:
        r = client.get(f'/truck/{tid}')
        assert r.status_code == 200, f'Truck view {tid} failed: {r.status_code}'
        assert tid.encode() in r.data
        print(f'GET /truck/{tid} -> OK (200)')

    # 3. Test Step API
    r3 = client.post('/api/step')
    assert r3.status_code == 200, f'Step API failed: {r3.status_code}'
    d3 = r3.get_json()
    assert d3['step'] == 1, f"Expected step 1, got {d3['step']}"
    print(f"POST /api/step -> OK (stepped to {d3['step']})")

    # 4. Test Step Again
    r3_2 = client.post('/api/step')
    d3_2 = r3_2.get_json()
    assert d3_2['step'] == 2, f"Expected step 2, got {d3_2['step']}"
    print(f"POST /api/step -> OK (stepped to {d3_2['step']})")

    # 5. Test Reset API
    r4 = client.post('/api/reset')
    assert r4.status_code == 200, f'Reset API failed: {r4.status_code}'
    d4 = r4.get_json()
    assert d4['step'] == 0, f"Expected step 0, got {d4['step']}"
    print(f"POST /api/reset -> OK (reset to {d4['step']})")

    # 6. Test Telemetry API
    r5 = client.get('/api/telemetry')
    assert r5.status_code == 200, f'Telemetry API failed: {r5.status_code}'
    d5 = r5.get_json()
    assert 'trucks' in d5
    assert len(d5['trucks']) == 4
    print('GET /api/telemetry -> OK')

    print('\nALL 6 TEST SUITES PASSED CLEANLY!')

if __name__ == '__main__':
    test_routes()
