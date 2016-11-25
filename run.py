#!flask/bin/python
import os
from app import myapp

port = int(os.environ.get('PORT', 5000))
myapp.run(debug=True,host='0.0.0.0', port=port)
