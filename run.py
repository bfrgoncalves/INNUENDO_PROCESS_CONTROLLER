#!flask/bin/python
from app import app

# app.run(debug=True, port=5001, threaded=True)
app.run(port=5001, threaded=True, host="0.0.0.0")


