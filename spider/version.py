

def toVersion(version, lts, os, arch, file_name, file_type, sum, sum_type, url, size):
    return {
        'version': version,
        'lts': lts,
        'os': os,
        'arch': arch,
        'file_name': file_name,
        'file_type': file_type,
        'sum': sum,
        'sum_type': sum_type,
        'url': url,
        'size': size
        }
