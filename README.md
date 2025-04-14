# ProxyChainer

ProxyChainer is a Python script similar to ProxyChains that allows you to force network connections through a chain of proxies. It supports HTTP and SOCKS proxies and provides a simple interface for users to specify which applications should use the proxy chain.

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Make the script executable (Linux/macOS):

```
chmod +x proxychainer.py
```

## Configuration

ProxyChainer uses a configuration file located at `~/.proxychainer.conf` by default. You can specify a different configuration file using the `-f` option.

The configuration file has the following format:

```ini
[ProxyChainer]
chain_type = strict
quiet_mode = off
proxy_dns = on

[ProxyList]
proxy1 = socks5 127.0.0.1 9050
proxy2 = http 192.168.1.1 8080
```

### Configuration Options

- `chain_type`: The type of proxy chaining to use (strict, dynamic, or random)
- `quiet_mode`: Whether to suppress output messages
- `proxy_dns`: Whether to proxy DNS requests

### Proxy List

The proxy list section contains the proxies to use in the chain. Each proxy is specified in the format:

```
proxy_name = proxy_type host port
```

Where:
- `proxy_name`: A unique name for the proxy
- `proxy_type`: The type of proxy (http, socks4, or socks5)
- `host`: The hostname or IP address of the proxy
- `port`: The port number of the proxy

## Usage

```
python proxychainer.py [options] [command]
```

### Options

- `-f, --config`: Path to the configuration file
- `-q, --quiet`: Quiet mode
- `-l, --list`: List the current proxy configuration

### Examples

List the current proxy configuration:

```
python proxychainer.py -l
```

Run a command through the proxy chain:

```
python proxychainer.py curl https://ifconfig.me
```

Use a specific configuration file:

```
python proxychainer.py -f /path/to/config.conf wget https://example.com
```

## Limitations

- The current implementation only uses the first proxy in the chain for simplicity
- Full proxy chaining requires a more complex implementation

## License

This project is licensed under the MIT License.