#!/usr/bin/env python3

import rsa;


(publicKey, privateKey) = rsa.newkeys(1024)
with open('keys/publcKey.pem', 'wb') as p:
    p.write(publicKey.save_pkcs1('PEM'))
with open('keys/privateKey.pem', 'wb') as p:
    p.write(privateKey.save_pkcs1('PEM'))
