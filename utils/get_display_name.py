from urllib.parse import urlparse

def get_display_name(url: str) -> str:
    try:
        domain = urlparse(url).netloc.lower()
        
        if domain.startswith("www."):
            domain = domain[4:]
        
        name = domain.split(".")[0]
        
        return name.capitalize()
    except:
        return url