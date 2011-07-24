Summary:        School Portal
Summary(ru):    Школьный портал
Name:           sp
Version:        4.1.3
Release:        %mkrel 1
License:        Prop
URL:            http://spcms.ru
Group:          Networking/WWW
Source0:        sp-for-rpm.tar.bz2
Source1:	.htaccess
Source2:	000-sp.conf
Source3:	CMS.gdb
Source4:	XXI.gdb
Source5:	UDFLib.dll
Source6:	update_xxi.pl
BuildRoot:      %{_tmppath}/%{name}-%{version}-root-dja
Requires:       task-lamp firebird-superserver perl-CGI perl-Archive-Zip perl-GD perl-GDGraph perl-Image-Magick perl-Mail-Sender perl-Text-Iconv perl-CPAN perl-CGI-Session perl-CGI-SpeedyCGI perl-HTML-TagFilter perl-DBD-InterBase

Autoprov:       0
Autoreq:        0

# Copyright:      Prop
# Если не задано Copyright, его значение берётся из License

# -------------------------------------------
# Описание на английском
# -------------------------------------------
%description
Integrated school control system.

# -------------------------------------------
# Описание на русском
# -------------------------------------------
%description -l ru
Комплексная система управления школой.

# -------------------------------------------
# Установка. Устанавливаем всё, что нужно в $RPM_BUILD_ROOT как в /
# -------------------------------------------
%install
rm -rf %{buildroot}
mkdir -p $RPM_BUILD_ROOT/var/www/cgi-bin/sp/
mkdir -p $RPM_BUILD_ROOT/var/www/html/sp/
mkdir -p $RPM_BUILD_ROOT/opt/xxi/data/
mkdir -p $RPM_BUILD_ROOT//etc/httpd/conf/vhosts.d/
mkdir -p $RPM_BUILD_ROOT/usr/lib/firebird/UDF/
mkdir -p $RPM_BUILD_ROOT/sbin/
#mkdir -p $RPM_BUILD_ROOT/usr/sbin/

cp %{SOURCE1}   $RPM_BUILD_ROOT/var/www/html/
cp %{SOURCE2} $RPM_BUILD_ROOT//etc/httpd/conf/vhosts.d/
cp %{_sourcedir}/*.gdb       $RPM_BUILD_ROOT/opt/xxi/data/
cp %{SOURCE5}  $RPM_BUILD_ROOT/usr/lib/firebird/UDF/UDFLib.dll

cd $RPM_BUILD_ROOT/var/www/cgi-bin/sp
tar xf %{_sourcedir}/sp-for-rpm.tar.bz2
cp %{SOURCE6} $RPM_BUILD_ROOT/var/www/cgi-bin/sp/update_xxi.pl

mv -f $RPM_BUILD_ROOT/var/www/cgi-bin/sp/sp_add_admin.pl $RPM_BUILD_ROOT/sbin/sp-add-admin

# -------------------------------------------
# Список файлов, которые попадут в пакет
# -------------------------------------------
%files
%defattr(400, root, root)
%config(noreplace) /var/www/cgi-bin/sp/sp.conf
%config(noreplace) /opt/xxi/data/*
/var/www/cgi-bin/sp/cms/
/var/www/cgi-bin/sp/dic/
/var/www/cgi-bin/sp/sphtml/
/var/www/cgi-bin/sp/tpl/
/var/www/cgi-bin/sp/*.cgi
/var/www/cgi-bin/sp/*.pl
/var/www/cgi-bin/sp/sp.sql
/var/www/cgi-bin/sp/*.ttf
/var/www/html/.htaccess
/etc/httpd/conf/vhosts.d/000-sp.conf
/usr/lib/firebird/UDF/UDFLib.dll
/sbin/sp-add-admin
#/sbin/sp-ldap-setup
#/usr/sbin/smbldap-passwd
#/var/www/cgi-bin/sp/smbldap-passwd

# -------------------------------------------
# Команды, выполняющиеся после распаковки файлов из пакета при установке на целевую систему
# -------------------------------------------
%post

# Прежде всего пофиксим неверную установку Firebird из RPM ALT Linux-а (для Mandriva проверить)

# без этого fb не видит свой конфиг
#chmod o+rx /etc/firebird
# без этого fb не соединяется с базой
#chmod g+w /etc/firebird

# для FB суперсервер - не юзается

#cd /etc/init.d/
#./firebird start
# /etc/init.d/firebird start
# не работает. apt-get ругается:
# The following packages have unmet dependencies:
#   sp: PreDepends: /etc/rc.d/init.d/firebird but it is not installable
# поэтому пока так

# для FB классик:

# снимаем ограничение на 5 коннектов к fb
#if ! grep -q "per_source = UNLIMITED" /etc/xinetd.d/firebird; then
#	perl -i -p -e 's/^\s*disable\s+=\s+no$/disable = no\nper_source = UNLIMITED/' /etc/xinetd.d/firebird
#fi

/etc/init.d/xinetd restart

rm -f -- /etc/httpd/conf/vhosts.d/00_default_vhosts.conf

/etc/init.d/httpd restart

# restore
#chown -R firebird:firebird /opt/xxi/data/
#chmod 660 /opt/xxi/data/*.*
#cd /usr/bin/
#./gbak -R -C /opt/xxi/data/XXI.gbk 127.0.0.1:/opt/xxi/data/XXI.gdb -USER sysdba -PASS masterkey
#./gbak -R -C /opt/xxi/data/CMS.gbk 127.0.0.1:/opt/xxi/data/CMS.gdb -USER sysdba -PASS masterkey
#rm -f -- /opt/xxi/data/*.gbk

chown -R firebird:firebird /opt/xxi/data/
chmod 660 /opt/xxi/data/*.*
chmod 755 /usr/lib/firebird/UDF/UDFLib.dll
chown apache.apache /var/www/html/.htaccess

cd /var/www/cgi-bin/sp/

perl setup.pl --yes

# Действие ($1)                     Значение параметра
# ====================================================
# Установка в первый раз            1
# Обновление                        2 или больше
# Удаление последней версии пакета  0

# выполнять только если установка в первый раз
if [ "$1" -eq 1 ]; then

	perl update_xxi.pl sp.conf sp.sql

fi

rm -f -- update_xxi.pl
rm -f -- sp.sql

chmod 500 /sbin/sp-add-admin

# выполнять только если установка в первый раз
if [ "$1" -eq 1 ]; then

	sp-add-admin admin smenimenya --silent
fi

chkconfig firebird on

echo '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
echo '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
echo '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
echo '!!!                                                                   !!!'
echo '!!!           School Portal installed.                                !!!'
echo '!!!           Administration account created.                         !!!'
echo '!!!           Direct your browser to this server to log in.           !!!'
echo '!!!                                                                   !!!'
echo '!!!           Login:    admin                                         !!!'
echo '!!!           password: smenimenya                                    !!!'
echo '!!!                                                                   !!!'
echo '!!!           CHANGE PASSWORD NOW!                                    !!!'
echo '!!!                                                                   !!!'
echo '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
echo '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
echo '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'

%clean
rm -rf %{buildroot}

