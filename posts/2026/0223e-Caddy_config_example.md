## Caddy config example

this is for caddy with cloudflare
- reverse proxy configuration
- https support with cloudflare dns resolving and LetsEncryt certificate

**home.domain.name should be set on cloudflare**

**subdomains should be maintained by local/home nameserver**

**subdomains should be pointed to caddy server**

**[API_KEY] should be replaced**

**domain.name should be replaced**

```
(log) {
	log {
		output file /var/log/caddy/access.log
	}
}

(common) {
	encode zstd gzip
	tls {
		dns cloudflare [API_KEY]
	}
}

(reverse) {
	@{args[0]} host {args[0]}.home.domain.name
	handle @{args[0]} {
		reverse_proxy {args[1]}:{args[2]}
	}
}

(reverse_tls) {
	@{args[0]} host {args[0]}.home.domain.name
	handle @{args[0]} {
		reverse_proxy {args[1]}:{args[2]} {
			transport http {
				tls
				tls_insecure_skip_verify
			}
		}
	}
}

*.home.domain.name {
#	import log
	import common

	@www host www.home.domain.name
	handle @www {
		root * /var/www
		file_server {
			hide .git
			hide .gitignore
		}
	}

	import reverse gitea    gitea.home.domain.name    8001
	import reverse jellyfin jellyfin.home.domain.name 8096

	handle {
		abort
	}
}
```

---

Date: 2026. 02. 23

Tags: caddy, cloudflare, letsencryt, config
