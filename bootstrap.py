from flask import Flask, request, abort, Response
from functools import wraps
import sys
import plistlib
import os
app = Flask(__name__)
try:
    if getenv('BOOTSTRAP_DEBUG').lower() == 'true':
        DEBUG = True
    else:
        DEBUG = False
except:
    DEBUG = False

try:
    my_username = os.getenv('BOOTSTRAP_USERNAME', 'admin')
except:
    my_username = 'admin'

try:
    my_password = os.getenv('BOOTSTRAP_PASSWORD', 'secret')
except:
    my_password = 'secret'

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == my_username and password == my_password

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/gen_manifest', methods = ['GET', 'POST'])
@requires_auth
def gen_manifest():
    build = request.form.get('build', None)
    site = request.form.get('site', None)
    serial = request.form.get('serial', None)
    # If we're re-imaging, these are required
    if build == None or site == None or serial == None:
        abort(403)

    # Currently we're assuming it's in the same directory as this script
    munki_repo = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                            'munki_repo')
    manifest_file = os.path.join(munki_repo, 'manifests', serial)

    # if the manifests dir doesn't exist, make it
    if not os.path.exists(os.path.join(munki_repo, 'manifests')):
        os.makedirs(os.path.join(munki_repo, 'manifests'))

    # if the manifest doesn't already exist set the catalog
    if not os.path.isfile(manifest_file):
        manifest = {}
        manifest['catalogs'] = ['production']
    else:
        manifest = plistlib.readPlist(manifest_file)
    manifest['included_manifests'] = ['site_default']
    if site:
        site_manifest = 'included_manifests/sites/%s' % site
        manifest['included_manifests'].append(site_manifest)
    if build:
        build_manifest = 'included_manifests/builds/%s' % build
        manifest['included_manifests'].append(build_manifest)
    plistlib.writePlist(manifest, manifest_file)

    return 'Manifest saved'

@app.route('/')
@requires_auth
def index():
    build = request.headers.get('X-bootstrap-build')
    site = request.headers.get('X-bootstrap-site')
    url = os.getenv('BOOTSTRAP_URL', 'http://localhost:5000')
    script = '''#!/usr/bin/python
import subprocess
import re
import urllib
import os

site='{0}'
build='{1}'
username='{2}'
password='{3}'
url='{4}'

def get_hardware_info():
    cmd = ['/usr/sbin/system_profiler', 'SPHardwareDataType', '-xml']
    proc = subprocess.Popen(cmd, shell=False, bufsize=-1,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, unused_error) = proc.communicate()
    try:
        plist = FoundationPlist.readPlistFromString(output)
        # system_profiler xml is an array
        sp_dict = plist[0]
        items = sp_dict['_items']
        sp_hardware_dict = items[0]
        return sp_hardware_dict
    except Exception:
        return {{}}

hardware_info = get_hardware_info()

serial = hardware_info.get('serial_number', 'UNKNOWN')
serial = re.sub('[^A-Za-z0-9]+', '', serial)
serial_lower = serial.lower()
username_and_password = username+':'+password
data = {{
'serial': serial,
'site': site,
'build': build
}}

cmd = ['/usr/bin/curl', '-u', username_and_password, '--data', urllib.urlencode(data), url+'/gen_manifest']
task = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

'''.format(site, build, my_username, my_password, url)
    return script

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=DEBUG)
