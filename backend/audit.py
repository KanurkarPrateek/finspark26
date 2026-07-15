"""
⑥ Tamper-Evident Audit Log
Hash-chained records, each signed with a post-quantum signature (ML-DSA-65, FIPS 204).
Rewriting any past record breaks the hash chain; forging a record is impossible without
the signing key — and the signature itself is quantum-safe.
"""
import base64
import hashlib
import json

from pqc import SIG


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


class AuditLog:
    def __init__(self):
        self._pk, self._sk = SIG.keygen()
        self.scheme = SIG.name
        self.pqc_active = SIG.active
        self.records = []

    def append(self, rtype, payload):
        prev = self.records[-1]["hash"] if self.records else "GENESIS"
        seq = len(self.records)
        body = _canon({"seq": seq, "type": rtype, "payload": payload, "prev": prev})
        h = hashlib.sha256(body.encode()).hexdigest()
        sig = base64.b64encode(SIG.sign(self._sk, h.encode())).decode()
        self.records.append(
            {"seq": seq, "type": rtype, "payload": payload, "prev": prev, "hash": h, "sig": sig}
        )

    def verify(self):
        prev = "GENESIS"
        for r in self.records:
            body = _canon({"seq": r["seq"], "type": r["type"], "payload": r["payload"], "prev": prev})
            recomputed = hashlib.sha256(body.encode()).hexdigest()
            hash_ok = recomputed == r["hash"]
            sig_ok = SIG.verify(self._pk, r["hash"].encode(), base64.b64decode(r["sig"]))
            if not (hash_ok and sig_ok):
                return {
                    "valid": False, "broken_at": r["seq"], "record_type": r["type"],
                    "reason": "record altered (hash mismatch)" if not hash_ok
                              else "signature invalid — cannot be re-signed without the private key",
                }
            prev = r["hash"]
        return {"valid": True, "count": len(self.records)}

    def tamper(self):
        """Demo: a malicious admin rewrites the backdoor alert to look routine."""
        for r in self.records:
            if r["type"] == "risk_decision" and "backdoor" in _canon(r["payload"]):
                r["payload"]["tier"] = "low"
                r["payload"]["reasons"] = ["routine maintenance window"]
                return {"tampered_seq": r["seq"],
                        "note": "Rewrote the backdoor-account alert to look like routine maintenance"}
        if len(self.records) > 1:
            self.records[1]["payload"] = {"note": "cover-up"}
            return {"tampered_seq": 1, "note": "Altered an audit record"}
        return {"tampered_seq": None, "note": "nothing to tamper yet"}
