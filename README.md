apmyph.py script will wait input for IP, username, password and sitename. Script will install apache web server to this server. After script will add virtualhost for sitename input. Then will print apache web server is ready and if you want to install configure MySQL with php just press Enter button. If you will click Enter MySQL and PHP5.6 with extensions will be installed and configured(MySQL root password is: freebsd). Then script will ask about database, username and password for new virtualhost. At the end script will create db user and pass for this virtualhost. If you will open page with http://virtualhostname you must see the installed MySQL version.

If you want to add new virtualhost just use add-vhost-apmyph.py script. Script will wait input for Apache server IP, username, pass and for virtualhost name. After that script will check virtualhost name on the web server. If this name is exists on the Apache web server, script will exit. If not exists, script will create all needs for this virtualhost.
