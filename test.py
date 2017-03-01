#!/usr/bin/env python3 -Wd
import os
import sys

from configparser import ConfigParser
from tempfile import mkstemp
from unittest import TestCase, main as test_main
from fs.fs import check_file_sha, compare_files, ensure_required_sections, \
    file_sync, make_backup_file, parse_args, read_config_file


class FileSyncTestCase(TestCase):
    def setUp(self):
        self.c = ConfigParser()
        self.c.read("filesync.conf")
        self.e = mkstemp()[1]
        self.f = ConfigParser()
        self.f.read("idkjaja")
        self.h = "localhost"

    def test_check_file_sha_returns_sha265sum(self):
        self.assertEqual(
            check_file_sha('filesync.conf', None).decode().split()[0],
            '315dc23cbcad8094dce9eec33fab67ff6cfc691e40bbae5cd4a9f3a2bf7c53ff')

    def test_check_file_sha_returns_false_for_fake_file(self):
        self.assertEqual(check_file_sha('idkjaja', None), False)

    def test_compare_files_equal(self):
        self.assertTrue(compare_files("foo", "foo"))

    def test_compare_files_not_equal(self):
        self.assertFalse(compare_files("foo", "bar"))

    def test_ensure_required_sections_fake_conf_file(self):
        self.assertFalse(ensure_required_sections(self.f))

    def test_ensure_required_sections_real_conf_file(self):
        self.assertTrue(ensure_required_sections(self.c))

    def test_file_sync_fake_file(self):
        f = "idkjaja"
        fs = file_sync("pull", f + "-new", f, host=self.h)
        self.assertTrue('rsync error' in fs)

    def test_file_sync_pull(self):
        f = mkstemp()[1]
        fs = file_sync("pull", f, f, host=self.h)
        os.remove(f)
        self.assertTrue(fs)

    def test_file_sync_push(self):
        f = mkstemp()[1]
        fs = file_sync("push", f, f, host=self.h)
        os.remove(f)
        self.assertTrue(fs)

    def test_make_backup_file(self):
        backup = make_backup_file("filesync.conf")
        self.assertTrue(os.path.isfile(backup))
        os.remove(backup)

    def test_make_backup_file_fake_file(self):
        backup = make_backup_file("idkjaja")
        self.assertFalse(backup)

    def test_make_backup_file_localhost(self):
        backup = make_backup_file(os.path.abspath("filesync.conf"),
                                  host=self.h)
        f = check_file_sha(backup, host=self.h).decode()
        self.assertIsInstance(f, str)
        os.remove(backup)

    def test_parse_args_clean(self):
        pass

    def test_parse_args_pull(self):
        pass

    def test_parse_args_push(self):
        pass

    def test_parse_args_host(self):
        pass

    def test_parse_args_conf(self):
        pass

    def test_parse_args_local_file_fake(self):
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = open('/dev/null', 'w')
        sys.stderr = open('/dev/null', 'w')
        with self.assertRaises(SystemExit):
            parse_args(["-L", "idkjaja", "--push"])
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    def test_parse_args_local_file_real(self):
        pass

    def test_parse_args_remote_file_fake(self):
        pass

    def test_parse_args_remote_file_real(self):
        pass

    def test_read_config_file_fake_file(self):
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = open('/dev/null', 'w')
        sys.stderr = open('/dev/null', 'w')
        with self.assertRaises(SystemExit):
            read_config_file("idkjaja")
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    def test_read_config_file_real_file(self):
        self.assertIsInstance(read_config_file("filesync.conf"), ConfigParser)

    def tearDown(self):
        os.remove(self.e)


if __name__ == '__main__':
    test_main()
