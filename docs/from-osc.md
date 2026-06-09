# Coming from `openstackclient`?

orca answers to **every** OSC verb word-for-word on the 10 core
services (Keystone, Nova, Neutron, Cinder, Glance, Designate,
Placement, Heat, Swift, Barbican) — 635/635 paths. Almost
everything you type in OSC works as-is. This page covers the
handful of differences that matter, and the orca-exclusive commands
that have no OSC equivalent.

## Drop-in replacement

```bash
# Anything you used to type with OSC works with orca:
orca server list
orca network create my-net --subnet-range 10.0.0.0/24
orca router add gateway my-router --network ext-net
orca volume backend pool list
orca zone export create example.com.
orca image add project <img> <proj>
orca trait show CUSTOM_NUMA_AWARE
```

If you have OSC muscle memory, run `alias openstack=orca` and you
won't notice — except things go faster (typed service layer,
parallel paginations, cached tokens).

## The few OSC paths that diverge (5)

These 5 commands can't share OSC's exact path because of a Click
framework limitation (a single name can't be both a leaf command
and a group). They route to the **same OpenStack API call** under
a slightly different orca path:

| OSC path | orca path | Same API call? |
|---|---|---|
| `server resize confirm <id>` | `server migration confirm <id>` | ✅ Nova `confirmResize` |
| `server resize revert <id>` | `server migration revert <id>` | ✅ Nova `revertResize` |
| `server backup create <id>` | `server backup <id>` | ✅ Nova `createBackup` |
| `image import info` | `image info import` | ✅ Glance `/v2/info/import` |
| `alarm-history search` | `alarm history <id>` | ✅ Aodh `/v2/alarms/{id}/history` |

## Breaking changes from earlier orca

If you upgraded an older orca install (≤ 2.6.0), 5 verbs were
refactored to match OSC:

| Before | Now |
|---|---|
| `volume backend capability HOST` | `volume backend capability show HOST` |
| `network flavor add FLAVOR PROFILE` | `network flavor add profile FLAVOR PROFILE` |
| `zone export ZONE` | `zone export create ZONE` |
| `zone import --file F` | `zone import create --file F` |
| `zone transfer accept TRANSFER KEY` | `zone transfer accept request TRANSFER KEY` |

## What you can do with orca that you can't with OSC

This is where orca pays for itself. None of these have a clean
OSC equivalent.

### `orca overview`

One screen with: VM count by status, FIP usage, volume usage,
quotas, recent events. Useful for "did anything change?"

```bash
orca overview
```

### `orca find <pattern>`

Cross-service grep across every resource you can see. Pass a
substring, IP address, or UUID prefix.

```bash
orca find 10.0.0.42        # which VM, port, FIP, FW has this IP?
orca find audit-           # every resource whose name starts with `audit-`
```

### `orca audit`

Resource inventory of the current project — counts, sizes,
suspicious patterns (orphaned ports, unused FIPs, snapshots over
N days, …). Read-only.

```bash
orca audit                 # human-readable summary
orca audit -f json         # for piping into another tool
```

### `orca cleanup`

Inverse of audit: actually delete the orphans, with explicit
confirmation and dry-run by default.

```bash
orca project cleanup --dry-run   # show what would be deleted
orca project cleanup --yes       # do it
```

### `orca server diff <id1> <id2>`

Compare two servers' metadata, flavor, networks, security groups
side-by-side. Useful when one VM works and another doesn't.

```bash
orca server diff <working-vm> <broken-vm>
```

### `orca server clone <id> --name <new>`

Boot a new VM with the same flavor / image / networks / keypair /
SGs as an existing one. Single command, no template needed.

```bash
orca server clone web-1 --name web-2
```

### `orca server bulk`

Create / delete many VMs with rate-limit and progress. Doesn't
need Heat.

```bash
orca server bulk create --count 10 --name-prefix worker- \
    --image debian-12 --flavor m1.small --network private
```

### `orca server port-forward <id> <local-port>:<remote-port>`

SSH-tunnel a port from your laptop into the VM through the
floating IP, with key resolution built in. Lighter than
`ssh -L … && nova ssh`.

### `orca subnet inspect <subnet>`

For a subnet, cross-reference availability, every port + its
owner (server / DHCP / router gateway / FIP), used IPs, free IPs.
Replaces 5 OSC calls.

### `orca network export <project> -o net.yaml`

Serialise a whole project's network topology (networks + subnets
+ ports + routers + SGs) into a single YAML file. Re-importable.

### `orca watch <command>`

Re-run any orca command every N seconds, with a Rich live diff.

```bash
orca watch server list -i 2     # refresh every 2 s
```

### `orca doctor`

Sanity-checks the current cloud: catalog endpoints reachable,
TLS valid, services up, common config errors. Same idea as
`brew doctor`.

### `orca profile`

Multi-cloud profile manager : `add`, `list`, `switch`,
`from-clouds` (import `clouds.yaml`), `from-openrc`, `to-clouds`
(export). No more sourcing rc files.

```bash
orca profile add prod    # interactive
orca profile switch prod
orca profile from-clouds # import existing clouds.yaml
```

## When orca is just nicer than OSC

Stuff that exists in OSC but reads better in orca:

* **`orca server create -i`** — interactive wizard with
  resource pickers (image / flavor / network / keypair), no
  flag chain.
* **`orca server create --wait`** — block until `ACTIVE`, with
  a progress bar.
* **`orca volume create --wait`** — same idea for Cinder.
* **`orca server snapshot <id> [--wait]`** — single verb instead
  of `openstack server image create … && openstack image show …
  --wait`.
* **`orca security-group rule add <sg> --proto tcp --port 22 --remote-ip 0.0.0.0/0`** —
  no JSON, no `--remote-group-id ''` boilerplate.
* **`orca floating-ip bulk-release`** — free every unattached FIP
  in one call.
* **`orca container save <name>`** — download an entire Swift
  container as a single tarball.
* **`orca zone tree <zone>`** — visualise a DNS zone with all
  its records as a tree.
* **`orca stack topology <stack>`** — Heat stack resource graph.

## Help, I can't find a command

orca's command tree is auto-registered. Use the standard help
to discover:

```bash
orca --help                # top-level groups
orca server --help         # everything under server
orca server add --help     # sub-group enumerator
```

Or grep through the static completion script:

```bash
orca completion show bash | grep -i <keyword>
```
