from io import BytesIO

import requests


def get_pdf(*, url):
    bio = BytesIO()
    with requests.get(url, stream=True) as rsp:
        rsp.raise_for_status()
        for chunk in rsp.iter_content(8192):
            bio.write(chunk)
    
    bio.seek(0)
    return bio.read()