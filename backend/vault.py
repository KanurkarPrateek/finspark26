"""
② Quantum-Safe Credential Vault

Credentials are encrypted with AES-256-GCM. The AES data-key is never stored — it
is protected by a post-quantum KEM (ML-KEM-768, FIPS 203): at rest we keep only the
KEM ciphertext, so an exfiltrated vault resists 'harvest-now-decrypt-later'. Without
the KEM decapsulation key an attacker (even a future quantum one) can't recover the key.
"""
import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from pqc import KEM


class QuantumSafeVault:
    def __init__(self):
        # Long-term KEM keypair; decaps key (self._dk) is the vault's root secret.
        self._ek, self._dk = KEM.keygen()
        # Encapsulate once to derive the AES data-key; store only the KEM ciphertext.
        shared, self._wrapped_key = KEM.encaps(self._ek)
        data_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                        info=b"vault-data-key").derive(shared)
        self._aes = AESGCM(data_key)

        self.scheme = KEM.name
        self.pqc_active = KEM.active
        self._store = {}  # system -> {username, nonce, ct}

        self.put("db-prod", "svc_dbprod", "S3cr3t-Prod-#2026")
        self.put("core-banking-admin", "cbadmin", "Adm!n-Core-9931")
        self.put("domain-controller", "DA_svc", "Dom@in-Adm-7745")
        self.put("payment-switch", "psw_ops", "Sw!tch-Ops-5520")

    def put(self, system, username, password):
        nonce = os.urandom(12)
        ct = self._aes.encrypt(nonce, password.encode(), system.encode())
        self._store[system] = {"username": username, "nonce": nonce, "ct": ct}

    def broker(self, system):
        """① Credential injection: decrypt + hand to the session. UI never sees raw secret."""
        rec = self._store.get(system)
        if not rec:
            return None
        pw = self._aes.decrypt(rec["nonce"], rec["ct"], system.encode()).decode()
        masked = pw[0] + "•" * (len(pw) - 2) + pw[-1]
        return {"username": rec["username"], "injected": True, "masked": masked}

    def exfiltrate(self):
        """Demo: everything a thief who steals the vault file gets — all useless ciphertext."""
        return {
            "scheme": self.scheme,
            "pqc_active": self.pqc_active,
            "wrapped_data_key_b64": base64.b64encode(self._wrapped_key).decode(),
            "credentials": {
                sys: {"username": r["username"],
                      "ciphertext_b64": base64.b64encode(r["ct"]).decode()}
                for sys, r in self._store.items()
            },
        }

    def systems(self):
        return list(self._store.keys())
