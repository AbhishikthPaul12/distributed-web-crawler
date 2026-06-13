from urllib.parse import urljoin, urlparse

def normalize_url(base_url, link):

    # Ignore empty links
    if not link:
        return None

    # Ignore javascript/mail links
    if link.startswith("javascript:"):
        return None

    if link.startswith("mailto:"):
        return None

    if link.startswith("tel:"):
        return None

    # Convert relative URL to absolute
    absolute_url = urljoin(base_url, link)

    # Remove fragments (#section)
    parsed = urlparse(absolute_url)

    cleaned_url = parsed.scheme + "://" + parsed.netloc + parsed.path

    return cleaned_url