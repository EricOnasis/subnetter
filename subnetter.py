#!/usr/bin/env python3
"""Subnet calculator with an allocation ledger for tracking who owns which subnet.

Usage:
    python subnetter.py info 10.0.4.0/24
    python subnetter.py split 10.0.0.0/22 --into 4
    python subnetter.py split 10.0.0.0/22 --prefix 24
    python subnetter.py alloc allocate 10.0.4.0/24 "customer-acme" --note "PPPoE pool"
    python subnetter.py alloc list
    python subnetter.py alloc free 10.0.4.0/24
"""
import argparse
import ipaddress
import json
import os

DEFAULT_LEDGER_PATH = "ledger.json"


def cmd_info(args):
    net = ipaddress.ip_network(args.cidr, strict=False)
    print(f"Network:      {net.network_address}")
    print(f"Netmask:      {net.netmask}")
    print(f"Wildcard:     {net.hostmask}")
    print(f"Prefix:       /{net.prefixlen}")
    print(f"Broadcast:    {net.broadcast_address if net.version == 4 else '-'}")
    hosts = list(net.hosts())
    if hosts:
        print(f"Usable range: {hosts[0]} - {hosts[-1]}")
    print(f"Total addrs:  {net.num_addresses}")
    print(f"Usable hosts: {max(net.num_addresses - 2, 0) if net.version == 4 else net.num_addresses}")
    print(f"Private:      {net.is_private}")


def cmd_split(args):
    net = ipaddress.ip_network(args.cidr, strict=False)

    if args.prefix is not None:
        new_prefix = args.prefix
    elif args.into is not None:
        bits_needed = (args.into - 1).bit_length()
        new_prefix = net.prefixlen + bits_needed
    else:
        raise SystemExit("Specify either --into N or --prefix N")

    if new_prefix < net.prefixlen:
        raise SystemExit(f"--prefix /{new_prefix} is larger than the supernet /{net.prefixlen}")

    subnets = list(net.subnets(new_prefix=new_prefix))
    if args.into is not None:
        subnets = subnets[: args.into]

    for sub in subnets:
        print(sub)


def load_ledger(path: str) -> dict:
    if not os.path.exists(path):
        return {"allocations": []}
    with open(path) as f:
        return json.load(f)


def save_ledger(path: str, ledger: dict) -> None:
    with open(path, "w") as f:
        json.dump(ledger, f, indent=2)


def find_overlap(ledger: dict, net: ipaddress._BaseNetwork):
    for entry in ledger["allocations"]:
        existing = ipaddress.ip_network(entry["cidr"])
        if net.overlaps(existing):
            return entry
    return None


def cmd_alloc_allocate(args):
    ledger = load_ledger(args.ledger)
    net = ipaddress.ip_network(args.cidr, strict=False)

    overlap = find_overlap(ledger, net)
    if overlap:
        raise SystemExit(
            f"{net} overlaps with existing allocation {overlap['cidr']} "
            f"(owner: {overlap['owner']})"
        )

    ledger["allocations"].append({
        "cidr": str(net),
        "owner": args.owner,
        "note": args.note or "",
    })
    save_ledger(args.ledger, ledger)
    print(f"Allocated {net} to {args.owner}")


def cmd_alloc_free(args):
    ledger = load_ledger(args.ledger)
    net = ipaddress.ip_network(args.cidr, strict=False)

    before = len(ledger["allocations"])
    ledger["allocations"] = [e for e in ledger["allocations"] if e["cidr"] != str(net)]

    if len(ledger["allocations"]) == before:
        raise SystemExit(f"No allocation found for {net}")

    save_ledger(args.ledger, ledger)
    print(f"Freed {net}")


def cmd_alloc_list(args):
    ledger = load_ledger(args.ledger)
    if not ledger["allocations"]:
        print("No allocations.")
        return
    for entry in sorted(ledger["allocations"], key=lambda e: ipaddress.ip_network(e["cidr"])):
        note = f" ({entry['note']})" if entry.get("note") else ""
        print(f"{entry['cidr']:<20} {entry['owner']}{note}")


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    info_p = sub.add_parser("info", help="Show details about a subnet")
    info_p.add_argument("cidr")
    info_p.set_defaults(func=cmd_info)

    split_p = sub.add_parser("split", help="Split a supernet into smaller subnets")
    split_p.add_argument("cidr")
    split_p.add_argument("--into", type=int, help="Split into at least N equally sized subnets")
    split_p.add_argument("--prefix", type=int, help="Split into subnets of this prefix length")
    split_p.set_defaults(func=cmd_split)

    alloc_p = sub.add_parser("alloc", help="Track subnet allocations in a local ledger")
    alloc_sub = alloc_p.add_subparsers(dest="alloc_command", required=True)

    allocate_p = alloc_sub.add_parser("allocate", help="Record a new allocation")
    allocate_p.add_argument("cidr")
    allocate_p.add_argument("owner")
    allocate_p.add_argument("--note", default="")
    allocate_p.add_argument("--ledger", default=DEFAULT_LEDGER_PATH)
    allocate_p.set_defaults(func=cmd_alloc_allocate)

    free_p = alloc_sub.add_parser("free", help="Remove an allocation")
    free_p.add_argument("cidr")
    free_p.add_argument("--ledger", default=DEFAULT_LEDGER_PATH)
    free_p.set_defaults(func=cmd_alloc_free)

    list_p = alloc_sub.add_parser("list", help="List all allocations")
    list_p.add_argument("--ledger", default=DEFAULT_LEDGER_PATH)
    list_p.set_defaults(func=cmd_alloc_list)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
