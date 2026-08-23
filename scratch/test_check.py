import sys
from app import create_app, db
from app.models import User
import json

app = create_app()

with app.app_context():
    client = app.test_client()
    
    # login
    user = User.query.filter_by(username='testuser').first()
    if not user:
        user = User(username='testuser')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
    res = client.post('/api/login', json={'username': 'testuser', 'password': 'password123'})
    print("Login:", res.status_code, res.json)
    
    # post check
    res = client.post('/api/topics/present_simple/practice/1/check', json={
        "answer": "She works in an office",
        "prompt": "Она работает в офисе."
    })
    
    print("Check Answer:", res.status_code)
    if res.status_code == 500:
        print(res.text)
        # To get the traceback, we can catch it by letting it crash without test_client handling, or just look at logs
