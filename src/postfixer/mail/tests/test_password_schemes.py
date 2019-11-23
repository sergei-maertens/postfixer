from django.test import SimpleTestCase

from ..password_schemes import check_password, hash_password

# Tested using doveadm pw -s <scheme>


class PasswordSchemesTests(SimpleTestCase):
    def test_plain(self):
        hashed = hash_password("dummy", scheme="PLAIN")
        self.assertTrue(hashed.startswith("{PLAIN}"))
        self.assertTrue(check_password("dummy", hashed))

        # implementation detail...
        self.assertEqual(hashed, "{PLAIN}dummy")

    def test_md5_crypt(self):
        hashed = hash_password("dummy", scheme="MD5-CRYPT")
        self.assertTrue(hashed.startswith("{MD5-CRYPT}$1$"))
        self.assertTrue(check_password("dummy", hashed))

    def test_sha256_bcrypt(self):
        hashed = "{SHA256-CRYPT}$5$pkgpGwMgaHDRrAEl$Cr/Yg.oOUo.pU0d1gxczew/HJFf.Cnl3Ce6359bgxz9"

        pw_ok = check_password("dummy", hashed)

        self.assertTrue(pw_ok)

    def test_sha512_bcrypt(self):
        hashed = hash_password("dummy", scheme="SHA512-CRYPT")
        print(hashed)
        self.assertTrue(hashed.startswith("{SHA512-CRYPT}$6$"))
        self.assertTrue(check_password("dummy", hashed))
