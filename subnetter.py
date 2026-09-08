#!/usr/bin/env python3
"""Subnet calculator.

Usage:
    python subnetter.py info 10.0.4.0/24
    python subnetter.py split 10.0.0.0/22 --into 4
    python subnetter.py split 10.0.0.0/22 --prefix 24
"""
import argparse
import ipaddress


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

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
