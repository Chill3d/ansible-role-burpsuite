import argparse
import filecmp
import os
import pexpect.popen_spawn
import shutil
import signal
import sys
import tempfile
import urllib.request

exit_status = 0

parser = argparse.ArgumentParser(description='Download the Burp Suite CA Certificate.')
parser.add_argument('burpdir', help='Burp Suite directory')
parser.add_argument('cacert', help='Path to download the CA certificate to.')
args = parser.parse_args()

java_path = os.path.join(args.burpdir, "jre/bin/java")
cacert_file = args.cacert

burp_jar_files = [ f for f in os.listdir(args.burpdir) if f.startswith("burpsuite_") and f.endswith(".jar")]

if len(burp_jar_files) == 0:
    print('Could not find burpsuite jar file in {burpdir}'.format(burpdir=burpdir))
    exit_status = 1    
else:
    try:
        burp_jar_path = os.path.join(args.burpdir, burp_jar_files[0])
        child = pexpect.popen_spawn.PopenSpawn('{java} -Djava.awt.headless=true -jar "{jar}"'.format(java=java_path, jar=burp_jar_path), encoding='UTF-8')
        child.logfile = sys.stdout


        child.expect('Proxy service started')

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            tmp_cacert_file = os.path.join(tmp_dir_name, "ca.der")
            urllib.request.urlretrieve("http://localhost:8080/cert", tmp_cacert_file)
            shutil.move(tmp_cacert_file, cacert_file)
            os.chmod(cacert_file, 0o644)
            print("CA certificate saved.")

    except Exception as e: 
        print(e)
        exit_status = 1
    finally:
        child.kill(signal.SIGTERM)

sys.exit(exit_status)
