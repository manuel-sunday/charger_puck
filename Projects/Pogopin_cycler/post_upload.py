Import("env")
import subprocess, sys, os

def after_upload(source, target, env):
    script = os.path.join(env.subst("$PROJECT_DIR"), "log_serial.py")
    port   = env.subst("$UPLOAD_PORT")
    print(f"\n>>> Launching serial logger on {port} ...")
    subprocess.Popen([sys.executable, script, port])

env.AddPostAction("upload", after_upload)
