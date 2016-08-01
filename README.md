<html>
<meta charset="utf-8">
This script for <b>FreeBSD 10></b> and <b>CentOS7></b> servers.

<b>apmyph.py</b> script will wait input for <b>IP</b>, <b>username</b>, <b>password</b> and <b>sitename</b>. It will install apache web server. After that script will add virtualhost for sitename input. Then it will print apache web server is ready and if you want to install configure MySQL with php just press <b>"Enter"</b> button. If you will click Enter, MySQL and PHP5.6 with extensions will be installed and configured(MySQL root password is: <b>freebsd</b>). Then script will ask about <b>database</b>, <b>username</b> and <b>password</b> for new virtualhost. At the end script will create database user and password for this virtualhost. If you will open page with <b>http://virtualhostname</b> you must see the installed MySQL version.

If you want to add new virtualhost just use <b>add-vhost-apmyph.py</b> script. Script will wait input for Apache server <b>IP</b>, <b>username</b>, <b>password</b> and for <b>virtual host</b> name. After that script will check virtualhost name on the web server. If this name is exists on the Apache web server, script will exit. If not exists, script will create all needs for this virtualhost.
</html>
