from app import app, client

res = client.post('/tutorials', json={"hyo": "1"})