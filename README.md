# Ox4Shell
Deobfuscate Log4Shell payloads with ease.


## Description
Since the release of the Log4Shell vulnerability (CVE-...), many tools were created to obfuscate Log4Shell payloads,
making the lifes of security engineers a nightmare.

This tool intends to aid security enginners to unravel the true contents of obfuscated Log4Shell payloads.


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

## Authors
- [Daniel Abeles](https://twitter.com/Daniel_Abeles)
- [Ron Vider](https://twitter.com/ron_vider)


## License
The source code for the site is licensed under the MIT license, which you can find in the LICENSE file.
