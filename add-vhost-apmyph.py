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
            print(' Apache web server installed and working...')
            domex = run('ls -la /usr/local/domen/ | grep '+sitename+' | awk \'{ print $9 }\' | cut -f1,2 -d \'.\'')
            if sitename == domex:
                print('Entered domain name '+sitename+' is already exists on the '+env.host_string+' server!!!')
                sys.exit()
            else:
                pass
            with open(sitename+".conf", "wb") as apvhostfile:
                apvhostfile.write(outputavText)
            put(sitename+'.conf', '/usr/local/domen/'+sitename+'.conf')
            with open("index.html", "wb") as aphtfile:
                aphtfile.write(outputahText)
            run('mkdir /var/www/'+sitename+'_public_html')
            put('index.html', '/var/www/'+sitename+'_public_html')
            run('/usr/local/etc/rc.d/apache24 restart')
            print('Virtualhost '+sitename+' already  configured...')
            print('If you want to configure database for '+sitename+' virtualhost just press "Enter"!!!')
            print('If you want to exit from script write "n" and press Enter button. ')
            inst = raw_input('Please select: ')
            if inst == "":
                print('You are selected "Enter" button')
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
                print('MySQL database for '+sitename+' already configured...')
            elif inst == "n":
                print('You entered "n" button.')
            else:
                print('You can only press "Enter" button or write "n" and after press enter button!!!')
        elif getfhttpdpack != '/usr/local/sbin/httpd' and httpdpidfile != httpdpid:
            print(' Apache web server is not working...')
    elif osver == 'Linux' and lintype == 'CentOS':
        print(' This is CentOS server...')
        getlhttpdpack = run('which httpd')
        httpdpidfile = run('cat /var/run/httpd/httpd.pid')
        httpdpid = run('ps waux | grep httpd | grep root | grep -v grep | awk \'{ print $2 }\'')
        if getlhttpdpack == '/usr/sbin/httpd' and httpdpidfile == httpdpid:
            print(' Apache web server installed and working...')
            domex = run('ls -la /usr/local/domen/ | grep '+sitename+' | awk \'{ print $9 }\' | cut -f1,2 -d \'.\'')
            if sitename == domex:
                print('Entered domain name '+sitename+' is already exists on the '+env.host_string+' server!!!')
                sys.exit()
            else:
                pass
            with open(sitename+".conf", "wb") as apvhostfile:
                apvhostfile.write(outputavText)
            put(sitename+'.conf', '/usr/local/domen/'+sitename+'.conf')
            with open("index.html", "wb") as aphtfile:
                aphtfile.write(outputahText)
            run('mkdir /var/www/'+sitename+'_public_html')
            put('index.html', '/var/www/'+sitename+'_public_html')
            run('systemctl restart httpd.service')
            print('Virtualhost '+sitename+' already  configured...')
            print('If you want to configure database for '+sitename+' virtualhost just press "Enter"!!!')
            print('If you want to exit from script write "n" and press Enter button. ')
            inst = raw_input('Please select: ')
            if inst == "":
                print('You are selected "Enter" button')
                msqlpidfile = run('ps waux|grep mysql | grep -v grep| grep -v safe | awk \'{ print $2 }\'')
                msqlpid = run('cat /var/run/mariadb/mariadb.pid')
                if msqlpidfile == msqlpid:
                    print('MySQL service already configured and running...')
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
                print('MySQL database for '+sitename+' already configured...')
            elif inst == "n":
                print('You entered "n" button.')
            else:
                print('You can only press "Enter" button or write "n" and after press enter button!!!')
        elif getlhttpdpack != '/usr/sbin/httpd' and httpdpidfile != httpdpid:
            print(' Apache web server is not working...')
            sys.exit()
