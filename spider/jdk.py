import os
import time
import requests
import json

from version import toVersion

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0'
}
majors = [8, 11, 16, 17, 18, 19, 20, 21, 22, 23]
versions_file_dir = 'versions/jdk/'
if not os.path.exists(versions_file_dir):
    os.makedirs(versions_file_dir)

versions = {}
updated = {}
if os.path.exists(f'{versions_file_dir}jdk-all.version.json'):
    versions = json.loads(open(f'{versions_file_dir}jdk-all.version.json', 'r').read())

def get_file_type(file_name):
    if file_name.endswith('.tar.gz'):
        return 'tar.gz'
    elif file_name.endswith('.tar.xz'):
        return 'tar.xz'
    else:
        strs = file_name.split('.')
        return strs[-1] if len(strs) > 1 else None

def push(version, lts, os, arch, checksum, size, url, file_name):
    file_type = get_file_type(file_name)
    if version in versions:
        for x in versions[version]:
            if x['sum'] == checksum:
                return
    else:
        versions[version] = []

    print(f'update {version}-{os}-{arch} {file_name} ...')

    updated['all'] = True
    updated[f'{os}-{arch}'] = True

    versions[version].append(toVersion(version, lts, os, arch, file_name, file_type, checksum, 'sha256', url, size))

def parse_data(data):
    version = data['release_name']
    lts = data['version_data']['optional'] == 'LTS' if 'optional' in data['version_data'] else False
    for binary in data['binaries']:
        if binary['image_type'] != 'jdk':
            continue
        os = binary['os']
        arch = binary['architecture']
        if 'installer' in binary:
            installer = binary['installer']
            checksum = installer['checksum']
            file_name = installer['name']
            size = installer['size']
            url = installer['link']
            push(version, lts, os, arch, checksum, size, url, file_name)
        if 'package' in binary:
            package = binary['package']
            checksum = package['checksum']
            file_name = package['name']
            size = package['size']
            url = package['link']
            push(version, lts, os, arch, checksum, size, url, file_name)


for major in majors:
    response = requests.get(f'https://api.adoptium.net/v3/assets/feature_releases/{major}/ga', headers=headers)
    datas = json.loads(response.text)
    for data in datas:
        parse_data(data)
    time.sleep(1)

for x in updated:
    if x == 'all':
        with open(f'{versions_file_dir}jdk-all.version.json', 'w') as f:
            json.dump(versions, f, indent=2)
        continue
    versions2 = {}
    for version in versions:
        versions2[version] = [v for v in versions[version] if (v['os'] + '-' + v['arch']) == x]
    with open(f'{versions_file_dir}jdk-{x}.version.json', 'w') as f:
        json.dump(versions2, f, indent=2)




