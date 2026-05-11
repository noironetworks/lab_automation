APIC_IP=$1
if [[ "${APIC_IP}" = "" ]]; then
   echo "Please specify an APIC IP"
   exit
fi
ROOT_CA_KEY_NAME=Internal-Root-CA.key
ROOT_CA_X509_NAME=Internal-Root-CA.pem
SIGNED_X509_CERT_NAME=apic_CA_signed.pem
CSR_NAME=apic.csr
VERIFY_SSL_KEY=adminuser.key
VERIFY_SSL_CERT=adminuser.crt

echo "Creating a client private key (${VERIFY_SSL_KEY}) and certificate (${VERIFY_SSL_CERT})"
openssl req -new -newkey rsa:2048 -days 36500 -nodes -x509 -keyout ${VERIFY_SSL_KEY} -out ${VERIFY_SSL_CERT} -subj "/CN=${APIC_IP}/O=Cisco Systems/C=US"
echo "Done!"
echo ""
echo "Creating a Root CA private key (${ROOT_CA_KEY_NAME})"
openssl ecparam -name secp384r1 -genkey -out ${ROOT_CA_KEY_NAME}
echo "Done!"
echo ""
echo "Creating a Root CA X.509 certificate, signed by the Root CA private key (${ROOT_CA_X509_NAME})"
openssl req -x509 -new -nodes -key ${ROOT_CA_KEY_NAME}  -sha256 -days 3650 -out ${ROOT_CA_X509_NAME} -config /etc/pki/tls/openssl.cnf -subj "/CN=${APIC_IP}/O=Cisco Systems/C=US"
echo "Done!"
echo ""
echo "Creating Certificate Signing Request (${CSR_NAME}), signed with client private key (${VERIFY_SSL_KEY})"
openssl req -new -key ${VERIFY_SSL_KEY} -out ${CSR_NAME} -config /etc/pki/tls/openssl.cnf -subj "/CN=${APIC_IP}/O=Cisco Systems/C=US"
echo "Done!"
echo ""
echo "Use the Root CA X.509 certificate (${ROOT_CA_X509_NAME}) and private key (${ROOT_CA_KEY_NAME}), along with the Certificate Signing Request (${CSR_NAME}) to create the signed certificate (${SIGNED_X509_CERT_NAME})"
openssl x509 -req -in ${CSR_NAME} -CA ${ROOT_CA_X509_NAME} -CAkey ${ROOT_CA_KEY_NAME}  -CAcreateserial -out ${SIGNED_X509_CERT_NAME} -days 365 -sha256 -extfile /etc/pki/tls/openssl.cnf -extensions v3_req
echo "Done!"
echo ""

echo "Add the ${VERIFY_SSL_CERT} to the client user in APIC (Admin => AAA => Users, edit user, Advanced Settings, and Add X.509 Certificate). The name for this cert should be used as the 'certificate_name' parameter for AIM"
echo "Upload the ${VERIFY_SSL_KEY} to the AIM container, and specify this file using the 'private_key_file' parameter in AIM"
echo "Upload the ${ROOT_CA_X509_NAME} file to the AIM container, and specify this file using the 'verify_ssl_certificate' parameter in AIM"
echo "Make sure that the AIM configuration has no value configured for 'apic_password'"
echo "Add the ${ROOT_CA_X509_NAME} certificate as the 'Certificate Authority' in APIC (Admin => AAA => Security => Certificate Authorites)"
echo "Create a key ring in APIC (Admin => AAA => Security => Key Ring), using ${VERIFY_SSL_KEY} as the private key and ${SIGNED_X509_CERT_NAME} as the certificate"
echo "Select the new key ring for the 'Admin KeyRing' (Fabric => Fabric Policies => Policies => Pod => Management Access => default => Web Access)"
