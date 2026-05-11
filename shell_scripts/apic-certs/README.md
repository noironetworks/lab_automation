This directory contains a shell script that can be used to
generate certificates and private keys for AIMs integration with APIC.

The script is run using:

<pre><code>$ ./create-certs.sh <IP of APIC>
</code></pre>

The script creates the following files:
* adminuser.key
  Client's Private key. This should be uploaded to the AIM container, and the AIM container should be configured with the path using 'private_key_file'
* adminuser.crt
  The client's X.509 Certificate. This should be installed in APIC, in the admin user (Admin => AAA => Users, edit user, Advanced Settings, and Add X.509 Certificate). The name for this cert should be used as the 'certificate_name' parameter for AIM
* Internal-Root-CA.key
  This file doesn't need to be installed anywhere - it's used for signing the Root CA X.509 certificate, as well as the shared signed X.509 certificate.
* Internal-Root-CA.pem
  Upload this file to the AIM container, and specify this path to the file using the 'verify_ssl_certificate' parameter in AIM. This file should also be used as the certificate in the Key Ring created in APIC (see below).
* apic_CA_signed.pem
  This certificate should be used when creating the Key Ring in APIC (see below).
* apic.csr
  This file doesn't need to be installed anywhere - it's used to create the shared signed X.509 certificate.


The process is this:

The client private key is used to create a Certificate Signing Request (CSR). The CSR is just a request to a Root Certificate Authority (CA)
that is used to generate a signed X.509 certificate, which both the client and server use to establish authentication. The client will also
use the private key to sign any messages sent to the server/APIC. APIC will be able to authenticate these messages because it has the matching
public key for the client (contained in the clients X.509 ceritifcate, adminuser.crt).

The server sends authentication messages to the client using the apic_CA_signed.pem X.509 certificate. Since this certificate was effectively
signed by both the client (via the client's CSR, which was signed by the client's private key) and the server (via the server's public and
private keys), the client can use the Root CA's public key (contained as part of the Root CA Internal-Root-CA.pem) to authenticate messages
from the server.

As an example, the following would be used the aim.conf file:
verify_ssl_certificate=/etc/aim/Internal-Root-CA.pem
private_key_file=/etc/aim/adminuser.key
certificate_name=admin
