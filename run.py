from webapp import app, celeryconfig

app.run(host='0.0.0.0', port=80, debug=True)
