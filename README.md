# subnetter

A CLI subnet calculator. No dependencies beyond the Python standard library.

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

An allocation ledger (tracking which subnet belongs to which customer/site) is coming soon.

## License

MIT — see [LICENSE](LICENSE).
