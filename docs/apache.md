# Open WebUI Configuration

## UI Configuration

For the UI configuration, you can set up the Apache VirtualHost as follows:

```
# Assuming you have a website hosting this UI at "server.com"
<VirtualHost 192.168.1.100:80>
    ServerName server.com
    DocumentRoot /home/server/public_html

    ProxyPass / http://server.com:3000/ nocanon
    ProxyPassReverse / http://server.com:3000/

</VirtualHost>
```

Enable the site first before you can request SSL:

`a2ensite server.com.conf` # this will enable the site. a2ensite is short for "Apache 2 Enable Site"

```
# For SSL
<VirtualHost 192.168.1.100:443>
    ServerName server.com
    DocumentRoot /home/server/public_html

    ProxyPass / http://server.com:3000/ nocanon
    ProxyPassReverse / http://server.com:3000/

    SSLEngine on
    SSLCertificateFile /etc/ssl/virtualmin/170514456861234/ssl.cert
    SSLCertificateKeyFile /etc/ssl/virtualmin/170514456861234/ssl.key
    SSLProtocol all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1

    SSLProxyEngine on
    SSLCACertificateFile /etc/ssl/virtualmin/170514456865864/ssl.ca
</VirtualHost>

```

I'm using virtualmin here for my SSL clusters, but you can also use certbot directly or your preferred SSL method. To use SSL:

### Prerequisites

Run the following commands:

`snap install certbot --classic`
`snap apt install python3-certbot-apache` (this will install the apache plugin).

Navigate to the apache sites-available directory:

`cd /etc/apache2/sites-available/`

Create server.com.conf if it is not yet already created, containing the above `<virtualhost>` configuration (it should match your case. Modify as necessary). Use the one without the SSL:

Once it's created, run `certbot --apache -d server.com`, this will request and add/create an SSL keys for you as well as create the server.com.le-ssl.conf
