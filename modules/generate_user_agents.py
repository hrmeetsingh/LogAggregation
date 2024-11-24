def generate_user_agents(count: int = 1, include_mobile: bool = True) -> List[str]:
    """
    Generate a list of random user agent strings.
    
    Args:
        count (int): Number of user agents to generate
        include_mobile (bool): Whether to include mobile user agents
        
    Returns:
        List[str]: List of generated user agent strings
    """
    
    browsers = {
        'chrome': {
            'versions': ['90.0.4430.212', '91.0.4472.124', '92.0.4515.159', '93.0.4577.82'],
            'template': 'Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36'
        },
        'firefox': {
            'versions': ['88.0', '89.0', '90.0', '91.0'],
            'template': 'Mozilla/5.0 ({os}; rv:{version}) Gecko/20100101 Firefox/{version}'
        },
        'safari': {
            'versions': ['14.1.1', '14.1.2', '15.0', '15.1'],
            'template': 'Mozilla/5.0 ({os}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15'
        }
    }
    
    desktop_os = [
        'Windows NT 10.0; Win64; x64',
        'Windows NT 6.1; Win64; x64',
        'Macintosh; Intel Mac OS X 10_15_7',
        'X11; Linux x86_64',
        'X11; Ubuntu; Linux x86_64'
    ]
    
    mobile_devices = [
        'iPhone; CPU iPhone OS 14_6 like Mac OS X',
        'Linux; Android 11; SM-G991B',
        'Linux; Android 10; SM-A505FN',
        'iPhone; CPU iPhone OS 15_0 like Mac OS X',
        'Linux; Android 12; Pixel 6'
    ]
    
    def generate_desktop_ua() -> str:
        """Generate a single desktop user agent."""
        browser = random.choice(list(browsers.values()))
        os_string = random.choice(desktop_os)
        version = random.choice(browser['versions'])
        return browser['template'].format(os=os_string, version=version)
    
    def generate_mobile_ua() -> str:
        """Generate a single mobile user agent."""
        browser = browsers['chrome']  # Most mobile browsers use Chrome-based engines
        device = random.choice(mobile_devices)
        version = random.choice(browser['versions'])
        return f"Mozilla/5.0 ({device}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Mobile Safari/537.36"
    
    user_agents = []
    for _ in range(count):
        if include_mobile and random.random() < 0.3:  # 30% chance of mobile user agent
            user_agents.append(generate_mobile_ua())
        else:
            user_agents.append(generate_desktop_ua())
            
    return user_agents