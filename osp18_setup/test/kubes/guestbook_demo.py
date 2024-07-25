import cobra.mit.access
import cobra.mit.session
#import cobra.model.fabric
from cobra.model.fv import Tenant,Ap,AEPg,RsPathAtt,BD,RsBd,Ctx,RsCtx,RsDomAtt,RsCons,RsProv
from cobra.model.vmm import DomP,ProvP
from cobra.model.pol import Uni
from cobra.model.vz import Filter,Entry,BrCP,Subj,RsSubjFiltAtt
from cobra.mit.request import ConfigRequest


ls = cobra.mit.session.LoginSession(
        'https://10.105.1.10', 'admin', 'cisco123')
md = cobra.mit.access.MoDirectory(ls)
md.login()

uniMo = Uni('')

t = Tenant(uniMo, 'kube01')
#ctx = Ctx(t, name='ifti_kube01-vrf')
ap = Ap(t, 'demo')

vmp = ProvP('uni', 'Kubernetes')
vdp = DomP(vmp, 'kube01')

#fmo = Filter(t, 'redis')

#enmo = Entry(fmo, 'redis')
#enmo.dFromPort = 6379   
#enmo.dToPort = 6379
#enmo.prot = 6          
#enmo.etherT = "ip"    

#vz1 = BrCP(t, 'redis')

#vsm = Subj(vz1, 'redis')
#RsSubjFiltAtt(vsm, tnVzFilterName=fmo.name)


print ("VMM_Dom = " + str(vdp.dn))

epg1 = AEPg(ap, 'demo-default')
RsDomAtt(epg1, vdp.dn)
RsCons(epg1, 'arp')
RsCons(epg1, 'icmp')
RsCons(epg1, 'dns')
RsBd(epg1, tnFvBDName='kube-pod-bd')
RsCons(epg1, 'kube01-l3out-allow-all')

epg2 = AEPg(ap, 'guestbook-frontend')
RsDomAtt(epg2, vdp.dn)
RsCons(epg2, 'credis')
RsProv(epg2, 'credis')
RsCons(epg2, 'arp')
RsCons(epg2, 'icmp')
RsCons(epg2, 'dns')
RsBd(epg2, tnFvBDName='kube-pod-bd')
RsCons(epg2, 'kube01-l3out-allow-all')

epg3 = AEPg(ap, 'guestbook-backend')
RsDomAtt(epg3, vdp.dn)
RsCons(epg3, 'credis')
RsProv(epg3, 'credis')
RsCons(epg3, 'arp')
RsCons(epg3, 'icmp')
RsBd(epg3, tnFvBDName='kube-pod-bd')
RsCons(epg3, 'dns')

c = ConfigRequest()
c.addMo(t)
md.commit(c)


ap = Ap(t, 'demo-netpol')
epg1 = AEPg(ap, 'demo-default')
RsDomAtt(epg1, vdp.dn)
RsCons(epg1, 'arp')
RsCons(epg1, 'icmp')
RsCons(epg1, 'dns')
RsBd(epg1, tnFvBDName='kube-pod-bd')
RsCons(epg1, 'kube01-l3out-allow-all')

c = ConfigRequest()
c.addMo(t)
md.commit(c)


