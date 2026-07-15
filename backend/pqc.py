"""
Post-Quantum Crypto adapter.

Uses the real NIST FIPS 203 / 204 algorithms when the pure-Python libraries are
installed, and transparently falls back to classical crypto otherwise so the app
always runs. `KEM.active` / `SIG.active` tell the UI which mode is live.

  KEM  — key encapsulation for the credential vault:  ML-KEM-768   (fallback: X25519)
  SIG  — signatures for the tamper-evident audit log:  ML-DSA-65    (fallback: Ed25519)

Interface (opaque byte/handle blobs — never mix impls):
  KEM.keygen() -> (ek, dk)
  KEM.encaps(ek) -> (shared_secret_bytes, ciphertext_bytes)
  KEM.decaps(dk, ciphertext_bytes) -> shared_secret_bytes
  SIG.keygen() -> (pk, sk)
  SIG.sign(sk, msg_bytes) -> sig_bytes
  SIG.verify(pk, msg_bytes, sig_bytes) -> bool
"""
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey)
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey, X25519PublicKey)


# ---------- Key encapsulation (vault) ----------
class _MLKEM:
    name = "ML-KEM-768 (FIPS 203)"
    active = True

    def __init__(self, impl):
        self._impl = impl

    def keygen(self):
        return self._impl.keygen()

    def encaps(self, ek):
        shared, ct = self._impl.encaps(ek)
        return shared, ct

    def decaps(self, dk, ct):
        return self._impl.decaps(dk, ct)


class _X25519KEM:
    name = "X25519 (classical fallback — install kyber-py for ML-KEM)"
    active = False

    def keygen(self):
        sk = X25519PrivateKey.generate()
        return sk.public_key().public_bytes_raw(), sk

    def encaps(self, ek):
        eph = X25519PrivateKey.generate()
        peer = X25519PublicKey.from_public_bytes(ek)
        return eph.exchange(peer), eph.public_key().public_bytes_raw()

    def decaps(self, dk, ct):
        return dk.exchange(X25519PublicKey.from_public_bytes(ct))


# ---------- Signatures (audit log) ----------
class _MLDSA:
    name = "ML-DSA-65 (FIPS 204)"
    active = True

    def __init__(self, impl):
        self._impl = impl

    def keygen(self):
        return self._impl.keygen()

    def sign(self, sk, msg):
        return self._impl.sign(sk, msg)

    def verify(self, pk, msg, sig):
        return self._impl.verify(pk, msg, sig)


class _Ed25519SIG:
    name = "Ed25519 (classical fallback — install dilithium-py for ML-DSA)"
    active = False

    def keygen(self):
        sk = Ed25519PrivateKey.generate()
        return sk.public_key().public_bytes_raw(), sk

    def sign(self, sk, msg):
        return sk.sign(msg)

    def verify(self, pk, msg, sig):
        try:
            Ed25519PublicKey.from_public_bytes(pk).verify(sig, msg)
            return True
        except Exception:
            return False


def _load_kem():
    try:
        from kyber_py.ml_kem import ML_KEM_768
        return _MLKEM(ML_KEM_768)
    except Exception:
        return _X25519KEM()


def _load_sig():
    try:
        from dilithium_py.ml_dsa import ML_DSA_65
        return _MLDSA(ML_DSA_65)
    except Exception:
        return _Ed25519SIG()


KEM = _load_kem()
SIG = _load_sig()
