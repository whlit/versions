import os
import time
import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0'
}
response = requests.get('https://nodejs.org/dist/index.json', headers=headers)

datas = json.loads(response.text)

versions_file_dir = 'versions/node/'
if not os.path.exists(versions_file_dir):
    os.makedirs(versions_file_dir)

def get_sums(version):
    url = 'https://nodejs.org/dist/v' + version + '/SHASUMS256.txt'
    print('request:  ' + url)
    resp = requests.get(url, headers=headers)
    res = {}
    for line in resp.text.split('\n'):
        if not line: continue
        [sum, name] = line.split('  ')
        res[name] = sum
    return res

versions = {}
if os.path.exists(versions_file_dir + 'node-all.version.json'):
    versions = json.loads(open(versions_file_dir + 'node-all.version.json', 'r').read())
sums = None
updated = {}

def get_file_name(version, os, arch, file_type):
    if file_type == 'exe':
        file_name = os + '-' + arch + '/node.exe'
    elif file_type == 'msi':
        file_name = 'node-v' + version + '-' + arch + '.msi'
    elif file_type == 'pkg':
        file_name = 'node-v' + version + '.pkg'
    else:
        file_name = 'node-v' + version + '-' + os + '-' + arch + '.' + file_type
    return file_name

def push(version, lts, os, arch, file_type):
    file_name = get_file_name(version, os, arch, file_type)

    if version in versions:
        for x in versions[version]:
            if x['file_name'] == file_name:
                return

    updated['all'] = True
    updated[os + '-' + arch] = True

    global sums
    if sums == None:
        sums = get_sums(version)
        time.sleep(1)

    if not version in versions:
        versions[version] = []

    versions[version].append({
                    'version': version,
                    'lts': lts,
                    'os': os,
                    'arch': arch,
                    'file_name': file_name,
                    'file_type': file_type,
                    'sum': sums[file_name],
                    'sum_type': 'sha256',
                    'url': 'https://nodejs.org/dist/v' + version + '/' + file_name
                    })

for data in datas:
    version = data['version'].replace('v', '')
    if version.startswith('0.'):
        continue
    lts =  True if data['lts'] else False
    sums = None
    for name in data['files']:
        if name.startswith('win'):
            strs = name.split('-')
            if len(strs) == 3:
                os = strs[0]
                arch = strs[1]
                file_type = strs[2]
                if file_type == 'msi':
                    push(version, lts, os, arch, 'msi')
                elif file_type == 'exe':
                    push(version, lts, os, arch, 'exe')
                else:
                    push(version, lts, os, arch, file_type)
        elif name.startswith('linux'):
            strs = name.split('-')
            if len(strs) == 2:
                os = strs[0]
                arch = strs[1]
                push(version, lts, os, arch, 'tar.gz')
                push(version, lts, os, arch, 'tar.xz')
        elif name.startswith('osx'):
            strs = name.split('-')
            if len(strs) == 3:
                file_type = strs[2]
                arch = strs[1]
                if file_type == 'pkg':
                    push(version, lts, 'darwin', 'any', 'pkg')
                else:
                    push(version, lts, 'darwin', arch, 'tar.gz')
                    push(version, lts, 'darwin', arch, 'tar.xz')


for x in updated:
    if x == 'all':
        with open(versions_file_dir + 'node-all.version.json', 'w') as f:
            json.dump(versions, f, indent=2)
        continue
    versions2 = {}
    for version in versions:
        versions2[version] = [v for v in versions[version] if (v['os'] + '-' + v['arch']) == x]
    with open(versions_file_dir + 'node-' + x + '.version.json', 'w') as f:
        json.dump(versions2, f, indent=2)

