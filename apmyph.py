#!/usr/bin/env python2.7

import sys
import os
import jinja2

from fabric.api import *
from fabric.tasks import execute
import getpass

templateLoader = jinja2.FileSystemLoader( searchpath="/" )
templateEnv = jinja2.Environment( loader=templateLoader )
TEMPAVFILE = os.getcwd()+'/jinja2temps/apvhost.conf'
TEMPHFILE = os.getcwd()+'/jinja2temps/tempindex.html'
TEMPPFILE = os.getcwd()+'/jinja2temps/tempindex.php'

tempav = templateEnv.get_template( TEMPAVFILE )
tempht = templateEnv.get_template( TEMPHFILE )
tempphp = templateEnv.get_template( TEMPPFILE )

env.host_string = raw_input('Please enter WEB server IP address: ')
env.user = raw_input('Please enter username for UNIX/Linux server: ')
env.password = getpass.getpass()
sitename = raw_input('Please enter site name: ')

tempavVars = { "sname" : sitename, "domain" : sitename, }

outputavText = tempav.render( tempavVars )
outputahText = tempht.render( tempavVars )

with settings(
        hide('warnings', 'running', 'stdout', 'stderr'), 
        warn_only=True
):
    osver = run('uname -s')
    lintype = run('cat /etc/redhat-release | awk \'{ print $1 }\'')
    ftype = run('uname -v | awk \'{ print $2 }\' | cut -f1 -d \'.\'')

    if osver == 'FreeBSD' and ftype >= 10:
        print(' This is FreeBSD server...')
        getfhttpdpack = run('which httpd')
        httpdpidfile = run('cat /var/run/httpd.pid')
        httpdpid = run('ps waux | grep httpd | grep root | grep -v grep | awk \'{ print $2 }\'')

        if getfhttpdpack == '/usr/local/sbin/httpd' and httpdpidfile == httpdpid:
            print(' You have already installed and running Apache web server...')
            print(' If you want add new VirtualHost, please use ./add-vhost-apmyph.py script. ')
            sys.exit()

        elif getfhttpdpack != '/usr/local/sbin/httpd':
            run('pkg install -y apache24')
            #run('echo \'apache24_enable="YES"\' >> /etc/rc.conf')
            run('sysrc apache24_enable="YES"')
            ip = run('ifconfig em0 | grep \'inet \' | awk \'{ print $2 }\'')
            name = run('hostname')
            run('echo \"'+ip+' '+name+'.lan '+name+'\" >> /etc/hosts')
            put(os.getcwd()+'/jinja2temps/fhttpd.conf', '/usr/local/etc/apache24/httpd.conf')
            run('mkdir -p /usr/local/domen /var/log/httpd/ /var/www/'+sitename+'_public_html')

            with open(sitename+".conf", "wb") as apvhostfile:
                apvhostfile.write(outputavText)

            put(sitename+'.conf', '/usr/local/domen/'+sitename+'.conf')

            with open("index.html", "wb") as aphtfile:
                aphtfile.write(outputahText)

            put('index.html', '/var/www/'+sitename+'_public_html')
            run('/usr/local/etc/rc.d/apache24 start')
            print('Apache server installed and configured...')
            print('If you want install and configure MySQL PHP just press "Enter"!!!')
            print('If you want to exit from script write "n" and press Enter button. ')
            inst = raw_input('Please select: ')

            if inst == "":
                print('You are selected "Enter" button')
                run('pkg install -y mysql55-server')
                run('pkg install -y mod_php56')
                run('pkg install -y php56-bz2 php56-mysql php56-mysqli php56-calendar php56-ctype php56-curl php56-dom php56-exif php56-fileinfo php56-filter php56-gd php56-gettext php56-hash php56-iconv php56-json php56-mbstring php56-mcrypt php56-openssl php56-posix php56-session php56-simplexml php56-tokenizer php56-wddx php56-xml php56-xmlreader php56-xmlwriter php56-xmlrpc php56-xsl php56-zip php56-zlib')
                put(os.getcwd()+'/jinja2temps/my.cnf', '/etc/my.cnf')
                put(os.getcwd()+'/jinja2temps/fphp.ini', '/usr/local/etc/php.ini')
                run('echo \'mysql_enable="YES"\' >> /etc/rc.conf')
                run('touch /var/log/mysql.log ; chown mysql:mysql /var/log/mysql.log')
                run('/usr/local/etc/rc.d/mysql-server start')
                run('echo -e "\n\nfreebsd\nfreebsd\n\n\n\n\n" | mysql_secure_installation 2>/dev/null')
                msqlpidfile = run('ps waux|grep mysql | grep -v grep| grep -v safe | awk \'{ print $2 }\'')
                msqlpid = run('cat /var/db/mysql/*.pid')

                if msqlpidfile == msqlpid:
                    print('MySQL service already running...')
                    pass
                else:
                    sys.exit()

                sitedb = raw_input('Enter name for new database: ')
                sitedbuser = raw_input('Enter new mysql user name: ')
                sitedbpasswd = getpass.getpass('Enter pass for '+sitedbuser+': ')
                sitedbpasswd1 = getpass.getpass('Repeat pass for '+sitedbuser+': ')

                if sitedbpasswd == sitedbpasswd1:
                    pass
                else:
                    print('The password for site db username must be the same!!! ')

                run('mysql -u root -p\'freebsd\' -e "CREATE DATABASE '+sitedb+';"')
                run('mysql -u root -p\'freebsd\' -e "GRANT ALL PRIVILEGES ON '+sitedb+'.* TO '+sitedbuser+'@localhost IDENTIFIED BY \''+sitedbpasswd+'\';"')
                run('mysql -u root -p\'freebsd\' -e "FLUSH PRIVILEGES;"')
                tempphVars = { "sitedb" : sitedb, "sitedbuser" : sitedbuser, "sitedbpasswd" : sitedbpasswd}
                outputphpText = tempphp.render( tempphVars )

                with open("index.php", "wb") as aphtfile:
                    aphtfile.write(outputphpText)

                put('index.php', '/var/www/'+sitename+'_public_html/index.php')
                run('/usr/local/etc/rc.d/apache24 restart')
                print('MySQL, Apache24 and PHP installed and configured...')

            elif inst == "n":
                print('You entered "n" button.')

            else:
                print('You can only press "Enter" button or write "n" and after press enter button!!!')

    elif osver == 'Linux' and lintype == 'CentOS':
        print(' This is CentOS server...')
        getlhttpdpack = run('which httpd')
        httpdpidfile = run('cat /var/run/httpd/httpd.pid')
        httpdpid = run('ps waux | grep httpd | grep root | grep -v grep | awk \'{ print $2 }\'')

        if getlhttpdpack == '/usr/sbin/httpd' and httpdpidfile == httpdpid:
            print(' You have already installed and running Apache web server...')
            print(' If you want add new VirtualHost, please use ./add-vhost-apmyph.py script')
            sys.exit()
        elif getlhttpdpack != '/usr/sbin/httpd':
            run('yum install -y httpd')
            ip = run('ifconfig `ifconfig | head -n1 | cut -f1 -d\':\'` | grep \'inet \' | awk \'{ print $2 }\'')
            name = run('hostname')
            run('echo \"'+ip+' '+name+'.lan '+name+'\" >> /etc/hosts')
            put(os.getcwd()+'/jinja2temps/c7httpd.conf', '/etc/httpd/conf/httpd.conf')
            run('mkdir -p /usr/local/domen /var/www/'+sitename+'_public_html')

            with open(sitename+".conf", "wb") as apvhostfile:
                apvhostfile.write(outputavText)

            put(sitename+'.conf', '/usr/local/domen/'+sitename+'.conf')

            with open("index.html", "wb") as aphtfile:
                aphtfile.write(outputahText)

            put('index.html', '/var/www/'+sitename+'_public_html')
            run('systemctl start httpd.service ; systemctl enable httpd.service')
            print('Apache server installed and configured...')
            print('If you want install and configure MySQL PHP just press "Enter"!!!')
            print('If you want to exit from script write "n" and press Enter button. ')
            inst = raw_input('Please select: ')

            if inst == "":
                print('You are selected "Enter" button')
                run('yum -y install mariadb-server mariadb')
                run('yum -y install php php-mysql')
                run('yum -y install php-bcmath.x86_64 php-cli.x86_64 php-gd.x86_64 php-mbstring.x86_64 php-xml.x86_64')
                put(os.getcwd()+'/jinja2temps/cmy.cnf', '/etc/my.cnf')
#                put(os.getcwd()+'/jinja2temps/fphp.ini', '/etc/php.ini')
                run('touch /var/log/mysql.log ; chown mysql:mysql /var/log/mysql.log')
                run('systemctl start mariadb ; systemctl enable mariadb')
                run('echo -e "\n\nfreebsd\nfreebsd\n\n\n\n\n" | mysql_secure_installation 2>/dev/null')
                msqlpidfile = run('ps waux|grep mysql | grep -v grep| grep -v safe | awk \'{ print $2 }\'')
                msqlpid = run('cat /var/run/mariadb/mariadb.pid')

                if msqlpidfile == msqlpid:
                    print('MySQL service already running...')
                    pass
                else:
                    print('MySQL service is not running...')
                    sys.exit()

                sitedb = raw_input('Enter name for new database: ')
                sitedbuser = raw_input('Enter new mysql user name: ')
                sitedbpasswd = getpass.getpass('Enter pass for '+sitedbuser+': ')
                sitedbpasswd1 = getpass.getpass('Repeat pass for '+sitedbuser+': ')

                if sitedbpasswd == sitedbpasswd1:
                    pass
                else:
                    print('The repeated password for '+sitedbuser+' must be the same!!! ')

                run('mysql -u root -p\'freebsd\' -e "CREATE DATABASE '+sitedb+';"')
                run('mysql -u root -p\'freebsd\' -e "GRANT ALL PRIVILEGES ON '+sitedb+'.* TO '+sitedbuser+'@localhost IDENTIFIED BY \''+sitedbpasswd+'\';"')
                run('mysql -u root -p\'freebsd\' -e "FLUSH PRIVILEGES;"')
                tempphVars = { "sitedb" : sitedb, "sitedbuser" : sitedbuser, "sitedbpasswd" : sitedbpasswd}
                outputphpText = tempphp.render( tempphVars )

                with open("index.php", "wb") as aphtfile:
                    aphtfile.write(outputphpText)
                put('index.php', '/var/www/'+sitename+'_public_html/index.php')
                run('systemctl restart httpd.service')
                print('MySQL, Apache24 and PHP installed and configured...')

            elif inst == "n":
                print('You entered "n" button.')

            else:
                print('You can only press "Enter" button or write "n" and after press enter button!!!')

    else:
        print(' This script supports FreeBSD or CentOS7 server...')
