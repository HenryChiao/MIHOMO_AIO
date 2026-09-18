# YENTA's 配置集


```yaml
chinaDNS: &chinaDNS ['223.5.5.5#DIRECT', '119.29.29.29#DIRECT']
  foreignDNS: &foreignDNS ['https://cloudflare-dns.com/dns-query#默认代理', 'https://dns.google/dns-query#默认代理']
  defaultDNS: &defaultDNS ['114.114.114.114#DIRECT', 'tls://223.5.5.5#DIRECT', 'https://1.12.12.12/dns-query#DIRECT']
  proxyServerDNS:
    &proxyServerDNS ['114.114.114.114#DIRECT', 'tls://223.5.5.5#DIRECT', 'https://doh.pub/dns-query#DIRECT']
```
