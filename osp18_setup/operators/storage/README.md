# Installation and Cleanup Guide
Please find the below mentioned yaml files at /home/stack/operators/storage path on the Fab-205 setup

## Prerequisites
Install the cert-manager Operator for Red Hat OpenShift by using the web console
### Sample Output
Given below is sample output post-installation of cert-manager Operator done via operator hub using the horizon
```
[stack@fab205-provision storage]$ oc get pods -n cert-manager-operator
NAME                                                        READY   STATUS    RESTARTS   AGE
cert-manager-operator-controller-manager-5f44f6fb47-462vg   2/2     Running   0          17m
[stack@fab205-provision storage]$ oc get pods -n cert-manager
NAME                                       READY   STATUS    RESTARTS   AGE
cert-manager-6f46f7dd96-pvxf2              1/1     Running   0          16m
cert-manager-cainjector-79b4758588-8vv44   1/1     Running   0          17m
cert-manager-webhook-67664c75f9-2zgkn      1/1     Running   0          17m
[stack@fab205-provision storage]$ 
```

## Installation Steps
```
sudo mkdir -p /var/hpvolumes
oc apply -f machine-config.yaml
oc apply -f hostpath_provisioner_namespace.yaml
oc apply -f webhook.yaml -n hostpath-provisioner
oc apply -f operator.yaml -n hostpath-provisioner
oc apply -f hostpathprovisioner.yaml
oc apply -f storageclass.yaml
oc apply -f cdi_operator.yaml
oc apply -f cdi_cr.yaml
oc apply -f demo_dv.yaml
```

## Cleanup Steps
```
oc delete dv dv_name -n default
oc delete -f hostpathprovisioner.yaml
oc delete -f storageclass.yaml
oc delete -f cdi_cr.yaml
oc delete -f cdi_operator.yaml
oc delete -f operator.yaml
oc delete -f webhook.yaml
oc delete -f hostpath_provisioner_namespace.yaml
oc delete -f machine-config.yaml
sudo rm -rf /var/hpvolumes
```

## Detailed Installation Steps
Let's jump into the installation steps for CSI

1. **Create Volume Directory on all the hosts**
   ```bash
   sudo mkdir -p /var/hpvolumes
2. **Set-selinux-for-hostpath-provisioner**
   ```bash
   oc apply -f machine-config.yaml
3. **Follow GitHub - https://github.com/kubevirt/hostpath-provisioner-operator - to install/create -**
   ```bash
   oc apply -f hostpath_provisioner_namespace.yaml
   oc apply -f webhook.yaml -n hostpath-provisioner
   oc apply -f operator.yaml -n hostpath-provisioner

If issue while getting hostpath-provisioner-operator pod up and running - please reapply "Issuer and Certificate" to avoid any kind of caBundle/Certificate Signed by Unknown Authority issue/s - and continue

```
cat <<EOF | oc apply -f -
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: selfsigned-issuer
  namespace: hostpath-provisioner
spec:
  selfSigned: {}
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  namespace: hostpath-provisioner
  name: hostpath-provisioner-operator-webhook-service-cert
  labels:
    name: hostpath-provisioner-operator
spec:
  secretName: hostpath-provisioner-operator-webhook-service-cert
  dnsNames:
  - hostpath-provisioner-operator-webhook-service.hostpath-provisioner.svc
  issuerRef:
    name: selfsigned-issuer
EOF   
```
4. **Apply the host path provisioner and storage class**
   ```bash
   oc apply -f hostpathprovisioner.yaml
   oc apply -f storageclass.yaml
5. **Download cdi-operator.yaml and cdi-cr.yaml from one of the latest release here - https://github.com/kubevirt/containerized-data-importer/releases**
   ```bash
   oc apply -f cdi_operator.yaml 
   oc apply -f cdi_cr.yaml
6. **Apply the data volume to see the creations of DV, PVC, PV**
   ```bash
   oc apply -f demo_dv.yaml

## Detailed Cleanup Steps
1. **Delete all the data volumes. Make sure to check - oc get (dv/pvc/pv) -A -o wide - all display "No resources found" before proceeding to next step, if not (anything missed) delete them manually**
   ```bash
   oc delete dv X -n default
2. **Follow the below delete steps in this order to do a neat cleanup**
   ```bash
   oc delete -f hostpathprovisioner.yaml
   oc delete -f storageclass.yaml
   oc delete -f cdi_cr.yaml
   oc delete -f cdi_operator.yaml
   oc delete -f operator.yaml
   oc delete -f webhook.yaml
   oc delete -f hostpath_provisioner_namespace.yaml
   oc delete -f machine-config.yaml
3. **Delete Volume Directory on all the hosts**
   ```bash
   sudo rm -rf /var/hpvolumes

### Sample Output
Given below is sample output post-installation of CSI

```
[stack@fab205-provision storage]$ oc get dv -A -o wide
NAMESPACE   NAME      PHASE       PROGRESS   RESTARTS   AGE
default     demo-dv   Succeeded   100.0%                3m14s
[stack@fab205-provision storage]$ oc get pvc -A -o wide
NAMESPACE   NAME      STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS           AGE     VOLUMEMODE
default     demo-dv   Bound    pvc-0b87fc56-8d81-4dec-b143-61c8a82b0e98   893Gi      RWO            hostpath-provisioner   3m15s   Filesystem
[stack@fab205-provision storage]$ oc get pv -A -o wide
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM             STORAGECLASS           REASON   AGE     VOLUMEMODE
pvc-0b87fc56-8d81-4dec-b143-61c8a82b0e98   893Gi      RWO            Delete           Bound    default/demo-dv   hostpath-provisioner            3m16s   Filesystem
[stack@fab205-provision storage]$  
```
```
[root@master1 core]# cd /var/hpvolumes
[root@master1 hpvolumes]# ls
csi
[root@master1 hpvolumes]# cd csi
[root@master1 csi]# ls
pvc-0b87fc56-8d81-4dec-b143-61c8a82b0e98
[root@master1 csi]# cd pvc-0b87fc56-8d81-4dec-b143-61c8a82b0e98/
[root@master1 pvc-0b87fc56-8d81-4dec-b143-61c8a82b0e98]# ls
disk.img
[root@master1 pvc-0b87fc56-8d81-4dec-b143-61c8a82b0e98]# 
```
