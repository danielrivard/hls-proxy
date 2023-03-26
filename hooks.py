hooks = {

}

def resource_replace(resource: bytes, root_url: bytes = b'') -> bytes:
    for old, new in hooks.items():
        resource = resource.replace(old, root_url + new)
    return resource
