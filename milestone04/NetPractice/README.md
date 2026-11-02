*This project has been created as part of the 42 curriculum by kyonaha.*

# NetPractice

## Description

NetPractice is a project about connecting networks. Each level shows a
small network that does not work, and the task is to change IP addresses,
subnet masks and routing tables so that the devices can communicate.
Shaded fields are fixed; only the unshaded fields can be changed.

At the top of each level, one or more **goals** say which devices must be
able to communicate. A level is cleared when every goal shows OK after
pressing **Check again**. There are 10 levels in total.

Through these exercises, the project teaches the basics of **TCP/IP
addressing**: how a subnet mask splits an address into a network part and
a host part, the role of the default gateway, and how routers and switches
connect networks.

## Instructions

### Running the training interface

1. Download the archive attached to the project page and extract it.
2. In the extracted folder, run:

   ```sh
   ./run.sh
   ```

   The script starts a local web server and opens the training page in
   the default web browser.
3. If `run.sh` does not work, start the server manually:

   ```sh
   python3 -m http.server 49242
   ```

   Then open `http://localhost:49242` in a web browser (any free port can
   be used).

On the welcome page, enter your 42 login before starting the levels:
each login gets its own configuration. The **evaluation** tab generates a
random configuration, which is the mode used during the defense.

### Exporting configurations

When a level is cleared, press **Get my config** before moving to the next
level. It downloads the configuration of the current level as
`levelN.json`, where `N` is the level number.

### Submission

- The repository must contain **10 exported configuration files, one per
  level** (`level1.json` to `level10.json`).
- All 10 files must be placed **at the root of the repository**, not in a
  subdirectory.
- This `README.md` must also be at the root of the repository.
- During the defense, three random levels must be solved within a limited
  time, without external tools (a simple calculator such as `bc` is
  tolerated).

## Resources

### References

I mainly studied with a study guide that I made with the help of AI
(see "How AI was used"). The guide was built on the following classic
references:

- Wendell Odom, *CCNA 200-301 Official Cert Guide*, Cisco Press — the
  chapters on subnetting and routing.
- Craig Hunt, *TCP/IP Network Administration*, O'Reilly — chapter 2
  (addressing).
- W. Richard Stevens, *TCP/IP Illustrated, Vol. 1*, Addison-Wesley — the
  chapters on IP.
- RFC 791 — *Internet Protocol* (IPv4).
  <https://www.rfc-editor.org/rfc/rfc791>
- RFC 950 — *Internet Standard Subnetting Procedure*.
  <https://www.rfc-editor.org/rfc/rfc950>
- RFC 1918 — *Address Allocation for Private Internets*.
  <https://www.rfc-editor.org/rfc/rfc1918>
- RFC 4632 — *Classless Inter-domain Routing (CIDR)*.
  <https://www.rfc-editor.org/rfc/rfc4632>
- The NetPractice subject (version 6.3).

Other 42 students also explained to me some concepts that I did not
understand well, such as routing tables.

### Networking concepts studied

#### TCP/IP addressing

An IPv4 address is a 32-bit number that identifies a device on a network.
It is split into four 8-bit **octets**, and each octet is written as a
decimal number from 0 to 255, separated by dots (for example
`192.168.1.10`).

An IP address is not given to a whole device but to each **interface**
(the point where the device connects to a network). A host usually has
one interface, while a router has one interface per network it is
connected to, so it has one IP address per interface.

#### Subnet mask and CIDR

A subnet mask splits an IP address into two parts: the **network part**,
which says which network the address belongs to, and the **host part**,
which identifies the interface inside that network.

The mask can be written in dotted form (`255.255.255.192`) or in CIDR
notation (`/26`). In CIDR notation, the number is how many bits, counted
from the left, belong to the network part: with `/26`, the first 26 bits
are the network part and the remaining 6 bits are the host part.

#### Network address and broadcast address

In each subnet, two addresses have a special meaning:

- the **network address**, where all host bits are 0. It refers to the
  whole network;
- the **broadcast address**, where all host bits are 1. A packet sent to
  it is addressed to every device on the network.

Because of these special meanings, neither of them can be assigned to an
interface.

#### Switch and router

- A **switch** works at layer 2 of the OSI model. It connects devices on
  the **same** network and forwards data by looking at MAC addresses.
- A **router** works at layer 3. It connects **different** networks and
  forwards packets by looking at IP addresses.

Each interface of a router must belong to a different network, and the
ranges of these networks must be mutually exclusive (they must not
overlap). If two ranges overlapped, one destination address would belong
to both networks, and the router could not decide which interface to send
the packet out of.

#### Routing table and default gateway

A routing table is a list of routes. Each route has two parts: a
**destination** and a **next hop**. The destination is a network, written
with only its network part (the host bits set to 0) and its mask, for
example `10.0.2.0/24`. The next hop is the full IP address of the
neighbouring device's interface, directly connected to this device, that
the packet is handed to. It is never the device's own address.

The destination `0.0.0.0/0` (written `default` in NetPractice) matches
every destination. The next hop of this route is the **default gateway**:
the device to which everything outside the local network is handed. For
a host, it is the IP address of the router interface that is on the same
network as the host.

A communication only works if the reply can also come back. The reply is
a new packet whose destination is the original sender, so every device on
the path needs a route for the way back as well as for the way there.

#### Private addresses and the Internet

Private addresses are ranges that are not assigned to anyone on the
Internet, so they can be freely reused inside any LAN. RFC 1918 reserves
three ranges: `10.0.0.0/8`, `172.16.0.0/12` (`172.16` to `172.31`) and
`192.168.0.0/16`.

Because many LANs reuse the same private ranges, a private destination
could not be resolved to a single place on the Internet, and routers
would not know where to send the packet. For this reason, private
addresses are not routed on the Internet.

A home PC with a private address can still communicate with the Internet
because the router changes the source IP address of its packets into the
router's own public address. This is called NAT; home routers use NAPT,
which also changes the port number so that many devices can share one
public address.

#### OSI model

The OSI model splits network communication into 7 layers. The TCP/IP
model was designed earlier: it was developed in the 1970s and adopted on
ARPANET in 1983, while the OSI model was published as ISO 7498 in 1984.

The TCP/IP model has 4 layers. The table shows how they match the 7 OSI
layers.

| OSI layer | Name | Examples | TCP/IP layer |
|---|---|---|---|
| 7 | Application | HTTP, DNS | Application |
| 6 | Presentation | Character encoding, encryption | Application |
| 5 | Session | Managing a conversation from start to end | Application |
| 4 | Transport | TCP, UDP | Transport |
| 3 | Network | IP, routers | Internet |
| 2 | Data link | MAC addresses, switches | Link |
| 1 | Physical | Cables, radio signals | Link |

Everything configured in NetPractice (IP addresses, masks and routes)
belongs to layer 3, the network layer.

### How AI was used

I used Claude for the following tasks:

- **Study guide**: Claude made a study guide in Japanese for me, following
  the structure of the references above (subnet calculation, routing,
  special addresses, the OSI model, exercises);
- **Understanding concepts**: I asked Claude questions about concepts such
  as broadcast, subnets, the default gateway and private addresses, and it
  explained them to me;
- **Debugging during practice**: when I was stuck on some levels (for
  example levels 6, 7 and 9), I showed screenshots and logs to Claude and
  asked it to explain which address or route was wrong and why. I then
  fixed the configuration in the training interface and made sure that I
  understood the reasoning;
- **Writing this README**: Claude asked me questions about each topic, and
  I answered them. When my answer was correct, Claude translated it into
  English and wrote it here; when it was wrong, Claude pointed out the
  mistake, and the corrected content was written after that.
