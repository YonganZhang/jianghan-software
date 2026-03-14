import subprocess, os, sys

os.makedirs('D:/projects/software/backend/logs', exist_ok=True)
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'

logfile = 'D:/projects/software/backend/logs/deploy.log'
log_out = open(logfile, 'w')

# CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
flags = 0x00000200 | 0x08000000

p = subprocess.Popen(
    [sys.executable, 'app.py'],
    cwd='D:/projects/software/backend',
    stdout=log_out, stderr=subprocess.STDOUT,
    env=env,
    creationflags=flags,
    close_fds=True,
)
print('PID:', p.pid)
