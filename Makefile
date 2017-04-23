VERSION = $$(grep VERSION\  fs/fs.py | awk -F\" '{ print  $$2 }')

.DEFAULT_GOAL:= exe

clean:
	@/bin/rm -fr build dist *.egg-info ./fs/__pycache__ ./fs/build ./fs/dist \
	filesync-* filesync-*.sha256sum ./fs/filesync.spec

exe:
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
