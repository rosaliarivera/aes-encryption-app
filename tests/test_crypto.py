import unittest
import json
import base64

from utils.crypto_utils import encrypt, decrypt, derive_key


class TestAESCrypto(unittest.TestCase):

    def setUp(self):
        self.plaintext = "Hello! This is an AES encryption test."
        self.password = "TestPassword123"

    def test_encryption_decryption(self):
        for mode in ["ECB", "CBC", "CFB"]:
            for key_bits in [128, 192, 256]:
                with self.subTest(mode=mode, key_bits=key_bits):
                    encrypted = encrypt(
                        self.plaintext,
                        self.password,
                        mode,
                        key_bits
                    )

                    decrypted = decrypt(
                        encrypted,
                        self.password
                    )

                    self.assertEqual(decrypted, self.plaintext)

    def test_unicode_text(self):
        plaintext = "Hola, España! Cifrado AES."

        encrypted = encrypt(
            plaintext, self.password, "CBC", 256
        )

        self.assertEqual(
            decrypt(encrypted, self.password),
            plaintext
        )

    def test_empty_plaintext(self):
        encrypted = encrypt(
            "", self.password, "CBC", 256
        )

        self.assertEqual(
            decrypt(encrypted, self.password),
            ""
        )

    def test_random_salt(self):
        first = json.loads(encrypt(
            self.plaintext, self.password, "CBC", 256
        ))

        second = json.loads(encrypt(
            self.plaintext, self.password, "CBC", 256
        ))

        self.assertNotEqual(first["salt"], second["salt"])

    def test_random_iv(self):
        for mode in ["CBC", "CFB"]:
            with self.subTest(mode=mode):
                first = json.loads(encrypt(
                    self.plaintext, self.password, mode, 256
                ))

                second = json.loads(encrypt(
                    self.plaintext, self.password, mode, 256
                ))

                self.assertNotEqual(first["iv"], second["iv"])

    def test_key_lengths(self):
        for key_bits in [128, 192, 256]:
            with self.subTest(key_bits=key_bits):
                key, salt = derive_key(
                    self.password, key_bits
                )

                self.assertEqual(len(key), key_bits // 8)
                self.assertEqual(len(salt), 16)

    def test_key_derivation_consistency(self):
        key1, salt = derive_key(self.password, 256)

        key2, _ = derive_key(
            self.password, 256, salt=salt
        )

        self.assertEqual(key1, key2)

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            encrypt(
                self.plaintext,
                self.password,
                "INVALID",
                256
            )

    def test_invalid_key_length(self):
        with self.assertRaises(ValueError):
            encrypt(
                self.plaintext,
                self.password,
                "CBC",
                64
            )

    def test_invalid_json(self):
        with self.assertRaises(json.JSONDecodeError):
            decrypt("invalid JSON", self.password)

    def test_payload_structure(self):
        payload = json.loads(encrypt(
            self.plaintext, self.password, "CBC", 256
        ))

        self.assertEqual(payload["mode"], "CBC")
        self.assertEqual(payload["key_bits"], 256)
        self.assertEqual(
            len(base64.b64decode(payload["salt"])), 16
        )
        self.assertEqual(
            len(base64.b64decode(payload["iv"])), 16
        )
        self.assertIn("ciphertext", payload)


if __name__ == "__main__":
    unittest.main()
