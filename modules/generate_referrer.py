def generate_referrer() -> str:
    """
    Generate a single random referrer URL.
    
    Returns:
        str: A generated referrer URL
    """
    
    # Common top-level domains
    tlds = ['com', 'org', 'net', 'edu', 'co.uk', 'io']
    
    # Common website names (without TLD)
    site_names = [
        'example',
        'website',
        'blog',
        'news',
        'tech',
        'digital',
        'online',
        'web',
        'info',
        'data',
        'dev',
        'code',
        'site',
        'portal'
    ]
    
    # Common subdomains
    subdomains = [
        'www',
        'blog',
        'news',
        'dev',
        'docs',
        ''  # Empty string for no subdomain
    ]
    
    # Common paths
    paths = [
        '',  # Root path
        'about',
        'contact',
        'news',
        'blog',
        'articles',
        'products',
        'services',
        'resources'
    ]
    
    # Generate URL components
    subdomain = random.choice(subdomains)
    site_name = random.choice(site_names)
    tld = random.choice(tlds)
    path = random.choice(paths)
    
    # Construct the URL
    url = 'https://'
    if subdomain:
        url += f'{subdomain}.'
    url += f'{site_name}.{tld}'
    if path:
        url += f'/{path}'
        
    return url