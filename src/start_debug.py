import sys, os, traceback, datetime

LOG = r'D:\projects\software\backend\logs\debug_start.log'
os.makedirs(os.path.dirname(LOG), exist_ok=True)

with open(LOG, 'w', encoding='utf-8') as f:
    f.write(f"=== Start at {datetime.datetime.now()} ===\n")
    f.write(f"Python: {sys.executable}\n")
    f.write(f"CWD: {os.getcwd()}\n")
    f.write(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'NOT SET')}\n")
    f.write(f"PATH (first 500): {os.environ.get('PATH', '')[:500]}\n")
    f.flush()

    try:
        os.chdir(r'D:\projects\software\backend')
        f.write(f"Changed CWD to: {os.getcwd()}\n")
        f.flush()

        # Redirect stdout/stderr to log
        sys.stdout = f
        sys.stderr = f
        os.environ['PYTHONIOENCODING'] = 'utf-8'

        f.write("About to import app module...\n")
        f.flush()

        # Try importing the app
        import app as flask_app
        f.write("App imported successfully\n")
        f.flush()

        # Try running
        f.write("Starting socketio.run...\n")
        f.flush()

        from exts import socketio
        with flask_app.app.app_context():
            flask_app.init_role_field(flask_app.app)
            flask_app.ensure_default_user()

        socketio.run(
            flask_app.app,
            debug=False,
            use_reloader=False,
            host='0.0.0.0',
            port=5000,
            allow_unsafe_werkzeug=True,
        )
    except Exception:
        f.write(f"\n=== EXCEPTION ===\n{traceback.format_exc()}\n")
        f.flush()
