all: export src-pkg bin-pkg clean

export:
	cd ..
	svn export https://bugbrother.svn.sourceforge.net/svnroot/bugbrother/sacam.py sacam-pkg

src-pkg:
	cd ..
	dpkg-source -b -i sacam-pkg

bin-pkg:
	sudo pbuilder build --buildresult ../ sacam_1.0.dsc

clean:
	cd ..
	rm -rf sacam-pkg
	mv sacam_1.0.* ../
