# subnetter

A CLI subnet calculator that goes one step past the usual toy calculators: it also tracks which
subnet is assigned to which customer or site, in a local JSON ledger, and refuses to let you
allocate something that overlaps an existing assignment.

No dependencies beyond the Python standard library.

## Usage

### Subnet info

```sh
python subnetter.py info 10.0.4.0/24
```

```
Network:      10.0.4.0
Netmask:      255.255.255.0
Wildcard:     0.0.0.255
Prefix:       /24
Broadcast:    10.0.4.255
Usable range: 10.0.4.1 - 10.0.4.254
Total addrs:  256
Usable hosts: 254
Private:      True
```

### Splitting a supernet

```sh
python subnetter.py split 10.0.0.0/22 --into 4     # split into (at least) 4 equal subnets
python subnetter.py split 10.0.0.0/22 --prefix 25   # split into /25s
```

### Allocation ledger

Track which subnet belongs to whom, and catch overlaps before they become an outage:

```sh
python subnetter.py alloc allocate 10.0.4.0/24 customer-acme --note "PPPoE pool"
python subnetter.py alloc allocate 10.0.5.0/24 customer-beta
python subnetter.py alloc list
```

```
10.0.4.0/24          customer-acme (PPPoE pool)
10.0.5.0/24          customer-beta
```

```sh
python subnetter.py alloc allocate 10.0.4.128/25 customer-gamma
```

```
10.0.4.128/25 overlaps with existing allocation 10.0.4.0/24 (owner: customer-acme)
```

Free an allocation when it's no longer in use:

```sh
python subnetter.py alloc free 10.0.4.0/24
```

The ledger defaults to `ledger.json` in the current directory; override with `--ledger path/to/file.json`
on any `alloc` subcommand. It's git-ignored by default since it's local operational state, not code.

## Running the tests

```sh
python -m unittest discover -s tests
```

## License

MIT — see [LICENSE](LICENSE).
