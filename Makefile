HAVE_PYINSTALLER = $(shell which pyinstaller 2>/dev/null && echo 0 || echo 1)
VERSION = $(shell grep VERSION\  fs/fs.py | awk -F\" '{ print  $$2 }')

.DEFAULT_GOAL:= exe

check_pyinstaller:
ifeq ($(HAVE_PYINSTALLER), 1)
	@echo PyInstaller is required to build an executable!
	@exit 1
endif

clean:
	@/bin/rm -fr build dist *.egg-info ./fs/__pycache__ ./fs/build ./fs/dist \
	filesync-* filesync-*.sha256sum ./fs/filesync.spec ./__pycache__

exe: check_pyinstaller
	@cd fs && \
	pyinstaller --name filesync --onefile fs.py && \
	cd .. && \
	mv fs/dist/filesync filesync-$(VERSION) && \
	sha256sum filesync-$(VERSION) > filesync-$(VERSION).sha256sum && \
	echo && echo BUILT: filesync-$(VERSION) AND filesync-$(VERSION).sha256sum

install:
	@pip3 install --compile --upgrade .

test:
	@python3 test.py
