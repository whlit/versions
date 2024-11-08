import json
import os
import time
from nbformat import versions
import requests
from lxml import etree

from version import toVersion


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0'
}

majors = [3, 4]
versions_file_dir = 'versions/maven/'
if not os.path.exists(versions_file_dir):
    os.makedirs(versions_file_dir)

versions = {}
updated = {}

def getSum(baseUrl):
    response = requests.get(f'{baseUrl}.sha512', headers=headers)
    return response.text

def push(version, lts, os, arch, checksum, size, url, file_name, file_type):
    if version in versions:
        for x in versions[version]:
            if x['sum'] == checksum:
                return
    else:
        versions[version] = []

    print(f'update {version}-{os}-{arch} {file_name} ...')

    updated['all'] = True

    versions[version].append(toVersion(version, lts, os, arch, file_name, file_type, checksum, 'sha512', url, size))

def getVersion(major, version):
    baseUrl = f'https://downloads.apache.org/maven/maven-{major}/{version}/binaries/'
    response = requests.get(baseUrl, headers=headers)
    html = etree.HTML(response.text)
    items = html.xpath('/html/body/pre/a/text()')
    for item in items:
        if not item.startswith('apache-maven-'):
            continue
        file_type = ''
        if item.endswith('.tar.gz'):
            file_type = 'tar.gz'
        elif item.endswith('.zip'):
            file_type = 'zip'
        else:
            continue
        file_name = item
        sum = getSum(f'{baseUrl}{item}')
        url = f'{baseUrl}{item}'
        push(version, False, 'any', 'any', sum, 0, url, file_name, file_type)
        time.sleep(0.2)


for major in majors:
    response = requests.get(f'https://downloads.apache.org/maven/maven-{major}', headers=headers)
    html = etree.HTML(response.text)
    vs = html.xpath('/html/body/pre/a/text()')
    for v in vs:
        if not v.startswith(str(major) + '.'):
            continue
        v = v.replace('/', '')
        getVersion(major, v)

if updated['all']:
    with open(versions_file_dir + 'maven.version.json', 'w') as f:
        json.dump(versions, f, indent=2)



