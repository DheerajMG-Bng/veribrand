"""Check tracked files for provider-key markers and .env files before pushing."""
import re
import subprocess

def main():
    marker='g'+'sk_'
    scan=subprocess.run(['git','grep','-n',marker],capture_output=True,text=True)
    if scan.returncode==0:
        raise SystemExit('Push stopped: provider key marker found. Output suppressed to protect secrets.')
    if scan.returncode!=1:
        raise SystemExit('Push stopped: secret scan did not complete.')
    tracked=subprocess.check_output(['git','ls-files'],text=True).splitlines()
    if any(re.search(r'(^|/)\.env$',path,re.I) for path in tracked):
        raise SystemExit('Push stopped: an environment file is tracked.')
    subprocess.run(['git','check-ignore','backend/.env'],check=True)
    print('PASS secret-marker scan; .env untracked and ignored.',flush=True)
    subprocess.run(['git','push'],check=True)

if __name__=='__main__':
    main()
