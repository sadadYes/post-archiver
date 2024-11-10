"""Proxy management functionality for YouTube Community Scraper"""

class ProxyManager:
    def __init__(self, proxy_file=None, single_proxy=None):
        self.current_index = 0
        self.proxies = []
        
        if proxy_file:
            with open(proxy_file) as f:
                self.proxies = [line.strip() for line in f if line.strip()]
        elif single_proxy:
            self.proxies = [single_proxy]
    
    def get_proxy_config(self, proxy_info):
        """Convert proxy string to Playwright proxy configuration."""
        # Extract scheme and other parts from proxy URL
        scheme = proxy_info['scheme']
        auth = f"{proxy_info['username']}:{proxy_info['password']}"
        host = proxy_info['host']
        port = proxy_info['port']
        
        return {
            'server': f'{scheme}://{host}:{port}',
            'username': proxy_info['username'],
            'password': proxy_info['password']
        }
    
    def get_next_proxy(self):
        """Get next proxy from the list and parse its components."""
        if not self.proxies:
            raise Exception("No proxies available")
            
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        # Parse proxy URL
        # Example: socks5://username:password@host:port
        try:
            scheme = proxy.split('://')[0]
            auth_host_port = proxy.split('://')[1]
            auth = auth_host_port.split('@')[0]
            host_port = auth_host_port.split('@')[1]
            username, password = auth.split(':')
            host, port = host_port.split(':')
            
            return {
                'scheme': scheme,
                'username': username,
                'password': password,
                'host': host,
                'port': port
            }
        except Exception as e:
            raise Exception(f"Failed to parse proxy URL: {proxy}") from e
