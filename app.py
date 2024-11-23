# app.py
from flask import Flask, render_template, jsonify, request
import threading
import time
import random
from datetime import datetime
import os
from queue import Queue
import json
from typing import List

app = Flask(__name__)

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Global variables to control log generation rates
log_rates = {
    'system': 0,
    'error': 0,
    'application': 0,
    'access': 0
}

LOG_MESSAGES = {
    'system': [
        # System Performance
        "CPU usage: {}% across {} cores",
        "Memory usage: {}MB / {}MB ({}% used)",
        "Disk space: {}GB free of {}GB total on {}",
        "Network bandwidth: {}Mbps ({}% utilization)",
        "Load average: {}, {}, {} (1/5/15 min)",
        "Swap usage: {}MB ({}% used)",
        "System uptime: {} days, {} hours",
        "Process count: {} running, {} sleeping",
        "Network connections: {} established, {} waiting",
        "IO operations: {} read/s, {} write/s",
        
        # System Events
        "System backup {} completed in {} minutes",
        "Scheduled maintenance starting in {} minutes",
        "Service {} restarted successfully",
        "System update available: version {}",
        "Firewall rule {} updated for port {}",
        "DNS cache cleared: {} entries removed",
        "Certificate {} renewed, expires in {} days",
        "Cron job {} completed with status {}",
        "System timezone updated to {}",
        "Hardware sensor: {} temperature at {}°C",
        
        # Resource Management
        "Cache hit ratio: {}% ({} hits/{} requests)",
        "Database connections: {} active, {} idle",
        "Thread pool: {} active, {} queued",
        "Storage volume {} mounted at {}",
        "Memory cleaned: {}MB recovered",
        "Network interface {} status changed to {}",
        "Power supply {} switched to {}",
        "Fan speed adjusted: {} RPM",
        "Temperature threshold adjusted: {}°C",
        "Virtual memory committed: {}GB"
    ],
    'error': [
        # Database Errors
        "Database connection timeout after {}ms on host {}",
        "Deadlock detected in transaction {}: tables involved {}",
        "Query execution failed: {} in procedure {}",
        "Database replication lag: {} seconds behind master",
        "Connection pool exhausted: {} waiting threads",
        "Foreign key constraint violation on table {}",
        "Database backup failed: {} - {}",
        "Invalid SQL syntax in query {}: {}",
        "Database index corruption detected on {}",
        "Transaction rollback triggered: {}",
        
        # Authentication/Authorization
        "Failed login attempt for user {} from IP {}",
        "Invalid JWT token: {} for user {}",
        "Permission denied: {} accessing {}",
        "Session validation failed: {}",
        "OAuth token expired for service {}",
        "Rate limit exceeded: {} requests from {}",
        "Invalid 2FA code attempted for user {}",
        "Password reset failed for account {}",
        "API key validation failed: {}",
        "CORS policy violation from origin {}",
        
        # Application Errors
        "NullPointerException in module {} line {}",
        "Memory leak detected in service {}: {}MB/hour",
        "Stack overflow in thread {}: {}",
        "Uncaught exception in {}: {}",
        "File system error: {} when accessing {}",
        "Cache corruption detected in region {}",
        "Configuration parse error in {}",
        "Template rendering failed: {}",
        "Serialization error for object {}",
        "Race condition detected in {}",
        
        # Network Errors
        "Connection refused to service {} on port {}",
        "DNS resolution failed for {}",
        "SSL/TLS handshake failed with {}",
        "Network timeout reaching {}:{}",
        "Invalid response from API {}: {}",
        "Load balancer health check failed for {}",
        "WebSocket connection terminated: {}",
        "HTTP/3 negotiation failed with {}",
        "gRPC stream error: {}",
        "MQTT broker connection lost: {}"
    ],
    'application': [
        # User Activities
        "User {} logged in from {} using {}",
        "Profile updated for user {}: fields {}",
        "New account registered: {} (referrer: {})",
        "Password changed for user {} from IP {}",
        "User {} enabled 2FA using {}",
        "Account {} deactivated: reason {}",
        "User preferences updated: {} for {}",
        "Session extended for user {}: {} minutes",
        "Login streak: {} days for user {}",
        "User {} joined group {}",
        
        # Transactions
        "Order #{} placed: {} items, total ${}",
        "Payment processed: ${} via {} for order {}",
        "Subscription renewed: plan {} for user {}",
        "Refund issued: ${} for order {}",
        "Invoice #{} generated for account {}",
        "Cart abandoned: {} items for user {}",
        "Discount code {} applied: saved ${}",
        "Recurring payment scheduled: {} for {}",
        "Payment failed: {} - Order #{}",
        "Wallet {} credited with {} points",
        
        # Content Management
        "Document {} uploaded by user {}",
        "Post #{} published in category {}",
        "Comment added to {} by user {}",
        "Media file {} processed: {}",
        "Content moderation: {} flagged as {}",
        "Article {} scheduled for {}",
        "Newsletter {} sent to {} subscribers",
        "Template {} updated by {}",
        "Asset {} archived: reason {}",
        "SEO metadata updated for {}",
        
        # System Operations
        "Cache invalidated for key {} by {}",
        "Background job {} completed in {}ms",
        "API version {} deployed to {}",
        "Feature flag {} enabled for {}",
        "Data export completed: {} records for {}",
        "Webhook {} delivered to {} successfully",
        "Batch process {} started with {} items",
        "Config {} updated in environment {}",
        "Service {} health check: {}",
        "Metric {} reported value {}"
    ],
    'access': [
        # Standard HTTP Methods
        "{} - {} [{}] \"GET {} HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"POST {} HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"PUT {} HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"DELETE {} HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"PATCH {} HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"OPTIONS {} HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"HEAD {} HTTP/1.1\" {} {} \"{}\" \"{}\"",
        
        # API Endpoints
        "{} - {} [{}] \"GET /api/v{}/users/{} HTTP/1.1\" {} \"{}\" \"{}\"",
        "{} - {} [{}] \"POST /api/v{}/auth/login HTTP/1.1\" {} \"{}\" \"{}\"",
        "{} - {} [{}] \"GET /api/v{}/products?page={} HTTP/1.1\" {} \"{}\" \"{}\"",
        "{} - {} [{}] \"PUT /api/v{}/users/{}/profile HTTP/1.1\" {} \"{}\" \"{}\"",
        "{} - {} [{}] \"DELETE /api/v{}/sessions/{} HTTP/1.1\" {} \"{}\" \"{}\"",
        "{} - {} [{}] \"POST /api/v{}/orders HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"GET /api/v{}/analytics/{} HTTP/1.1\" {} \"{}\" \"{}\"",
        
        # Static Assets
        "{} - {} [{}] \"GET /static/css/{}.css HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"GET /static/js/{}.js HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"GET /static/img/{}.{} HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"GET /assets/fonts/{}.woff2 HTTP/1.1\" {} {} \"{}\" \"{}\"",
        
        # Special Routes
        "{} - {} [{}] \"GET /health HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"GET /metrics HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"POST /webhooks/{} HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"GET /sitemap.xml HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"GET /robots.txt HTTP/1.1\" {} {} \"{}\" \"{}\"",
        "{} - {} [{}] \"GET /swagger/v{}/api-docs HTTP/1.1\" {} {} \"{}\" \"{}\"",
    ]
}


# Message templates
# LOG_MESSAGES = {
#     'system': [
#         "System health check completed",
#         "CPU usage: {}%",
#         "Memory usage: {}MB",
#         "Disk space remaining: {}GB",
#         "Network bandwidth: {}Mbps",
#         "Background tasks: {} running",
#         "Cache hit ratio: {}%",
#         "System temperature: {}°C",
#         "Power consumption: {}W",
#         "Active users: {}"
#     ],
#     'error': [
#         "Database connection failed: timeout after {}ms",
#         "Authentication failed for user: {}",
#         "Invalid request parameter: {}",
#         "Service {} unavailable",
#         "Memory leak detected in module: {}",
#         "File not found: {}",
#         "Permission denied for resource: {}",
#         "Rate limit exceeded for IP: {}",
#         "Uncaught exception in thread: {}",
#         "API version {} is deprecated"
#     ],
#     'application': [
#         "User {} logged in successfully",
#         "New account created: {}",
#         "Payment processed for order #{}",
#         "Email sent to {}",
#         "Profile updated for user {}",
#         "Data export completed for {}",
#         "Search query executed: {}",
#         "Configuration updated: {}",
#         "Cache invalidated for key: {}",
#         "Scheduled task completed: {}"
#     ],
#     'access': [
#         "{} - {} [{}] \"GET /api/users HTTP/1.1\" {} {}",
#         "{} - {} [{}] \"POST /api/login HTTP/1.1\" {} {}",
#         "{} - {} [{}] \"GET /api/products HTTP/1.1\" {} {}",
#         "{} - {} [{}] \"PUT /api/orders HTTP/1.1\" {} {}",
#         "{} - {} [{}] \"DELETE /api/sessions HTTP/1.1\" {} {}",
#         "{} - {} [{}] \"GET /api/stats HTTP/1.1\" {} {}",
#         "{} - {} [{}] \"POST /api/uploads HTTP/1.1\" {} {}",
#         "{} - {} [{}] \"GET /api/search HTTP/1.1\" {} {}",
#         "{} - {} [{}] \"PUT /api/profiles HTTP/1.1\" {} {}",
#         "{} - {} [{}] \"GET /api/health HTTP/1.1\" {} {}"
#     ]
# }

# def generate_log_entry(log_type):
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
#     message_template = random.choice(LOG_MESSAGES[log_type])
    
#     if log_type == 'system':
#         message = message_template.format(
#             random.randint(0, 100) if '{}%' in message_template
#             else random.randint(100, 1000) if '{}MB' in message_template
#             else random.randint(50, 500) if '{}GB' in message_template
#             else random.randint(100, 1000) if '{}Mbps' in message_template
#             else random.randint(1, 20) if '{} running' in message_template
#             else random.randint(50, 99) if '{}%' in message_template
#             else random.randint(30, 80) if '{}°C' in message_template
#             else random.randint(200, 500) if '{}W' in message_template
#             else random.randint(1, 1000)
#         )
#         return f"{timestamp} [SYSTEM] {message}"
    
#     elif log_type == 'error':
#         message = message_template.format(
#             random.randint(1000, 5000) if '{}ms' in message_template
#             else f"user_{random.randint(1000, 9999)}" if 'user: {}' in message_template
#             else f"param_{random.randint(1, 100)}" if 'parameter: {}' in message_template
#             else f"service_{random.randint(1, 10)}" if 'Service {}' in message_template
#             else f"module_{random.randint(1, 20)}" if 'module: {}' in message_template
#             else f"/path/to/file_{random.randint(1, 100)}.txt" if 'File not found: {}' in message_template
#             else f"resource_{random.randint(1, 50)}" if 'resource: {}' in message_template
#             else f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}" if 'IP: {}' in message_template
#             else f"Thread-{random.randint(1, 100)}" if 'thread: {}' in message_template
#             else f"v{random.randint(1, 5)}.{random.randint(0, 9)}"
#         )
#         return f"{timestamp} [ERROR] {message}"
    
#     elif log_type == 'application':
#         message = message_template.format(
#             f"user_{random.randint(1000, 9999)}" if 'user {}' in message_template or 'User {}' in message_template
#             else f"account_{random.randint(1000, 9999)}" if 'account created: {}' in message_template
#             else f"{random.randint(10000, 99999)}" if 'order #{}' in message_template
#             else f"user{random.randint(1, 1000)}@example.com" if 'Email sent to {}' in message_template
#             else f"profile_{random.randint(1, 1000)}" if 'Profile updated for user {}' in message_template
#             else f"export_{random.randint(1, 100)}" if 'Data export completed for {}' in message_template
#             else f"query_{random.randint(1, 100)}" if 'Search query executed: {}' in message_template
#             else f"config_{random.randint(1, 50)}" if 'Configuration updated: {}' in message_template
#             else f"cache_key_{random.randint(1, 1000)}" if 'Cache invalidated for key: {}' in message_template
#             else f"task_{random.randint(1, 100)}"
#         )
#         return f"{timestamp} [INFO] {message}"
    
#     else:  # access log
#         ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
#         user = f"user_{random.randint(1000,9999)}"
#         status = random.choice([200, 201, 204, 400, 401, 403, 404, 500])
#         bytes_sent = random.randint(500, 5000)
#         return message_template.format(ip, user, timestamp, status, bytes_sent)


################################################################################################

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


################################################################################################


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


################################################################################################

def generate_log_entry(log_type):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    message_template = random.choice(LOG_MESSAGES[log_type])
    
    if log_type == 'system':
        # Complex system log formatting
        message = message_template.format(
            *(random.randint(0, 100) for _ in range(message_template.count('{}')))
            if '%' in message_template
            else random.randint(100, 1000) if 'MB' in message_template
            else random.randint(50, 500) if 'GB' in message_template
            else random.randint(100, 1000) if 'Mbps' in message_template
            else f"service_{random.randint(1, 20)}" if 'service' in message_template.lower()
            else random.randint(1, 20)
        )
        return f"{timestamp} [SYSTEM] {message}"
    
    elif log_type == 'error':
        # Enhanced error log formatting
        error_codes = ['E_1001', 'E_1002', 'E_2001', 'E_3001', 'E_4001']
        services = ['auth', 'db', 'cache', 'api', 'web']
        error_types = ['ValidationError', 'TimeoutError', 'ConnectionError', 'SecurityError']
        
        message = message_template.format(
            random.choice(error_codes),
            random.choice(services),
            random.choice(error_types),
            f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            random.randint(1000, 9999)
        )
        return f"{timestamp} [ERROR] {message}"
    
    elif log_type == 'application':
        # Enhanced application log formatting
        users = [f"user_{random.randint(1000, 9999)}" for _ in range(5)]
        actions = ['created', 'updated', 'deleted', 'viewed', 'shared']
        resources = ['post', 'comment', 'profile', 'document', 'settings']
        
        message = message_template.format(
            random.choice(users),
            random.choice(actions),
            random.choice(resources),
            random.randint(1, 1000)
        )
        return f"{timestamp} [INFO] {message}"
    
    else:  # access log
        ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        user = f"user_{random.randint(1000,9999)}"
        status = random.choice([200, 201, 204, 301, 302, 304, 400, 401, 403, 404, 500, 502, 503])
        bytes_sent = random.randint(500, 150000)
        path = f"/api/v{random.randint(1,3)}/{random.choice(['users', 'posts', 'comments', 'products'])}/{random.randint(1,1000)}"
        referer = generate_referrer()
        user_agent = generate_user_agents(1)[0]
        
        return message_template.format(
            ip, user, timestamp, path, status, bytes_sent, referer, user_agent
        )

def log_writer():
    while True:
        for log_type, rate in log_rates.items():
            if rate > 0:
                # Calculate sleep time based on rate (0-100)
                # Rate of 100 = 10 logs per second, Rate of 1 = 1 log per 10 seconds
                messages_per_second = (rate / 10)
                if messages_per_second > 0:
                    sleep_time = 1 / messages_per_second
                    log_entry = generate_log_entry(log_type)
                    with open(f'logs/{log_type}.log', 'a') as f:
                        f.write(log_entry + '\n')
                        f.flush()
                    time.sleep(sleep_time)
        time.sleep(0.1)  # Small sleep to prevent CPU hogging

# Start the log writer thread
log_writer_thread = threading.Thread(target=log_writer, daemon=True)
log_writer_thread.start()

@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/update_rates', methods=['POST'])
def update_rates():
    global log_rates
    data = request.get_json()
    log_rates.update(data)
    return jsonify({'status': 'success', 'rates': log_rates})

@app.route('/get_rates', methods=['GET'])
def get_rates():
    return jsonify(log_rates)

if __name__ == '__main__':
    app.run(debug=True)