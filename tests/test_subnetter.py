import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from subnetter import cmd_alloc_allocate, cmd_alloc_free, find_overlap, load_ledger


class Args:
    """Minimal stand-in for argparse.Namespace."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)  # start with no file, like a fresh ledger
        self.ledger_path = self.tmp.name

    def tearDown(self):
        if os.path.exists(self.ledger_path):
            os.unlink(self.ledger_path)

    def test_allocate_and_list(self):
        cmd_alloc_allocate(Args(cidr="10.0.4.0/24", owner="acme", note="", ledger=self.ledger_path))
        ledger = load_ledger(self.ledger_path)
        self.assertEqual(len(ledger["allocations"]), 1)
        self.assertEqual(ledger["allocations"][0]["owner"], "acme")

    def test_overlap_is_rejected(self):
        cmd_alloc_allocate(Args(cidr="10.0.4.0/24", owner="acme", note="", ledger=self.ledger_path))
        with self.assertRaises(SystemExit):
            cmd_alloc_allocate(Args(cidr="10.0.4.128/25", owner="other", note="",
                                     ledger=self.ledger_path))

    def test_non_overlapping_allocations_both_succeed(self):
        cmd_alloc_allocate(Args(cidr="10.0.4.0/24", owner="acme", note="", ledger=self.ledger_path))
        cmd_alloc_allocate(Args(cidr="10.0.5.0/24", owner="beta", note="", ledger=self.ledger_path))
        ledger = load_ledger(self.ledger_path)
        self.assertEqual(len(ledger["allocations"]), 2)

    def test_free_removes_allocation(self):
        cmd_alloc_allocate(Args(cidr="10.0.4.0/24", owner="acme", note="", ledger=self.ledger_path))
        cmd_alloc_free(Args(cidr="10.0.4.0/24", ledger=self.ledger_path))
        ledger = load_ledger(self.ledger_path)
        self.assertEqual(ledger["allocations"], [])

    def test_free_unknown_subnet_raises(self):
        with self.assertRaises(SystemExit):
            cmd_alloc_free(Args(cidr="10.0.9.0/24", ledger=self.ledger_path))

    def test_find_overlap_returns_none_when_clear(self):
        import ipaddress
        ledger = {"allocations": [{"cidr": "10.0.4.0/24", "owner": "acme"}]}
        self.assertIsNone(find_overlap(ledger, ipaddress.ip_network("10.0.5.0/24")))


if __name__ == "__main__":
    unittest.main()
