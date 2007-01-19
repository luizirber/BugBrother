prep_po:
	intltool-extract --type=gettext/glade glade/sacam.glade
	xgettext --language=Python --keyword=_ --keyword=N_ --output=po/sacam.pot sacam/*.py glade/sacam.glade.h
	rm glade/sacam.glade.h

merge:
	msgmerge -U po/pt_BR.po po/sacam.pot
	
install:
	msgfmt --output-file=/usr/share/locale/pt_BR/LC_MESSAGES/sacam.mo po/pt_BR.po
	chown root:root /usr/share/locale/pt_BR/LC_MESSAGES/sacam.mo
	dpkg-reconfigure locales
