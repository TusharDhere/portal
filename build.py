import re,glob,html,json,os,sys
BASE=os.path.dirname(os.path.abspath(__file__))
LOCAL='--local' in sys.argv
from bs4 import BeautifulSoup
E=html.escape
SRC=os.path.join(BASE,'source')+os.sep
parts=[]
for f in sorted(glob.glob(SRC+'part-*.html')):
    n=int(re.search(r'part-(\d+)',f).group(1)); p=f'p{n:02d}'
    s=BeautifulSoup(open(f,encoding='utf8').read(),'html.parser'); m=s.select_one('main#content')
    for sel in ['.page-topbar','.part-pager','.footer','footer']:
        for e in m.select(sel): e.decompose()
    for e in m.select('div.mermaid'): e.name='pre'
    for e in m.find_all(id=True): e['id']=f'{p}-{e["id"]}'
    for a in m.find_all('a',href=True):
        h=a['href']; mm=re.match(r'(?:\./)?part-(\d+)-',h)
        if mm: a['href']='#p%02d'%int(mm.group(1))
        elif h.startswith('#'): a['href']='#'+p+'-'+h[1:]; a['data-t']=p+'-'+h[1:]
    for t in m.find_all('table'):
        w=s.new_tag('div',attrs={'class':'tw'}); t.wrap(w)
    h1=m.find('h1'); title=h1.get_text(strip=True); short=title.split('—',1)[-1].strip()
    h2=[(h['id'],h.get_text(' ',strip=True)) for h in m.find_all('h2')]
    toc='<nav class="toc">'+''.join(f'<a href="#{p}" data-t="{i}">{E(t)}</a>' for i,t in h2)+'</nav>'
    h1.insert_after(BeautifulSoup(toc,'html.parser'))
    parts.append(dict(n=n,p=p,short=short,title=title,body=m.decode_contents(),h2=len(h2)))

SOPS=[
dict(id='rg',cat='Governance',t='Create a Resource Group',p='Create a logical container for related resources with consistent name, region and tags.',c=['Resource group'],
 pre=['Azure subscription','Contributor or Owner on the subscription','Naming convention, e.g. rg-&lt;workload&gt;-&lt;env&gt;-&lt;region&gt;-001','Required tags (owner, cost-center, environment)'],
 arch='flowchart TD\n T[Tenant] --> MG[Management group] --> S[Subscription] --> RG[Resource group] --> R[Resources]',
 nav=['Resource groups','Create'],
 st=['Select <b>Subscription</b>.','Enter <b>Resource group</b> name.','Select <b>Region</b> (holds metadata only; resources may live elsewhere).','On <b>Tags</b>, add the mandatory tags.','Select <b>Review + create</b>, then <b>Create</b>.'],
 v=['Resource groups list shows the new group.','Resource group → Activity log shows a successful Create event.'],
 rb=['Resource group → Delete resource group → type the name. This deletes every resource inside it.'],
 ts=['AuthorizationFailed => missing role at subscription scope; check Access control (IAM).','Request blocked by policy => Policy → Compliance, find the denying assignment.','Name already exists => names are unique per subscription; change the name.'],
 d=['https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resource-groups-portal']),
dict(id='vm',cat='Compute',t='Create an Azure Virtual Machine',p='Deploy a VM with a secure network, sized disk and a safe remote-access method.',c=['Resource group','Virtual network and subnet','NIC','Public IP (optional)','Network security group','OS disk','Virtual machine'],
 pre=['Subscription and Contributor on the resource group','Region and Availability zone decision','VM size and quota available in region','Image (Marketplace or custom)','SSH key or password policy','Network plan: VNet, subnet, inbound rules'],
 arch='flowchart TD\n I[Internet or Bastion] --> PIP[Public IP] --> NSG[NSG] --> NIC[NIC] --> VM[VM] --> SN[Subnet] --> VN[VNet]',
 nav=['Virtual machines','Create','Azure virtual machine'],
 st=['<b>Basics</b>: Subscription, Resource group, VM name, Region, Availability options (zone), Security type, Image, Size.','<b>Basics</b>: Authentication type (SSH public key recommended for Linux), username. Set Inbound ports to <b>None</b> if you will use Bastion.','<b>Disks</b>: OS disk type; add data disks if required.','<b>Networking</b>: choose Virtual network and Subnet, Public IP (None for private VMs), NIC network security group.','<b>Management</b>: enable Boot diagnostics, Auto-shutdown for non-production, Defender for Cloud as policy requires.','<b>Monitoring</b> and <b>Advanced</b>: extensions, cloud-init if needed. <b>Tags</b>: add mandatory tags.','Select <b>Review + create</b>, wait for Validation passed, then <b>Create</b>.'],
 v=['VM → Overview shows Status: Running.','Connect via SSH/RDP/Bastion.','VM → Networking → Effective security rules shows only intended ports.'],
 rb=['Delete the VM, then its OS disk, NIC and public IP, or delete the whole resource group for a lab.'],
 ts=['SkuNotAvailable or QuotaExceeded => choose another size or zone, or Subscriptions → Usage + quotas to request an increase.','Cannot connect => check NSG rule, VM firewall, public IP and Boot diagnostics → Serial console.','Deployment failed => Resource group → Deployments → open the failed deployment for the error.'],
 d=['https://learn.microsoft.com/en-us/azure/virtual-machines/linux/quick-create-portal']),
dict(id='st',cat='Storage',t='Create a Storage Account and Upload a Blob',p='Create a secure general-purpose v2 account, then store a file in a private container.',c=['Storage account','Blob container','Blob'],
 pre=['Contributor on the resource group','Globally unique name: 3-24 lowercase letters and numbers','Redundancy decision (LRS, ZRS, GRS, GZRS)','Network access decision (public, selected networks, private endpoint)'],
 arch='flowchart TD\n U[Client] --> FW[Storage firewall or Private endpoint] --> SA[Storage account] --> C[Container] --> B[Blob]',
 nav=['Storage accounts','Create'],
 st=['<b>Basics</b>: Subscription, Resource group, Storage account name, Region, Performance (Standard), Redundancy.','<b>Advanced</b>: keep secure transfer on, minimum TLS 1.2, anonymous access disabled, default access tier Hot.','<b>Networking</b>: choose public access from selected networks or add a private endpoint.','<b>Data protection</b>: enable soft delete for blobs and containers; consider versioning.','<b>Review + create</b>, then <b>Create</b>.','Open the account → <b>Data storage</b> → <b>Containers</b> → <b>+ Container</b>; set anonymous access to Private.','Open the container → <b>Upload</b> → select file → <b>Upload</b>.'],
 v=['Container lists the blob with size and tier.','Blob → Overview → Properties show the URL; unauthenticated access returns an error as intended.'],
 rb=['Delete the blob, container or account. Soft delete may allow recovery within the retention period.'],
 ts=['Name not available => storage names are global; change it.','403 AuthorizationFailure => check storage firewall, your IP and RBAC role (Storage Blob Data Contributor).','Upload blocked in portal => add your client IP to the firewall or use a private network path.'],
 d=['https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create','https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-portal']),
dict(id='rbac',cat='Identity',t='Assign an Azure RBAC Role',p='Grant least-privilege access to a user, group or managed identity at the correct scope.',c=['Role assignment'],
 pre=['Owner, User Access Administrator or Role Based Access Control Administrator at the scope','Principal (prefer a group)','Role name and scope decided'],
 arch='flowchart TD\n P[User, group or identity] --> RA[Role assignment] --> SC[Scope: MG, subscription, RG, resource]',
 nav=['Open the target scope (subscription, resource group or resource)','Access control (IAM)','Add','Add role assignment'],
 st=['On <b>Role</b>, search and select the job-function or privileged role.','On <b>Members</b>, choose <b>User, group, or service principal</b> (or <b>Managed identity</b>) and <b>Select members</b>.','Optionally add a condition or description.','Select <b>Review + assign</b>.'],
 v=['Access control (IAM) → <b>Role assignments</b> lists the principal.','Use <b>Check access</b> for the principal to confirm effective roles.'],
 rb=['Role assignments → select the row → Remove.'],
 ts=['Add is greyed out => you lack roleAssignments/write at this scope.','Access not effective => allow a few minutes; the user may need to sign out and in.','Deny assignment or policy => review Deny assignments tab.'],
 d=['https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-portal']),
dict(id='net',cat='Networking',t='Create a VNet, Subnet and NSG',p='Build a network address space, a subnet and a rule set that controls traffic.',c=['Virtual network','Subnet','Network security group','Security rules'],
 pre=['Non-overlapping address space (e.g. 10.10.0.0/16)','Subnet plan (e.g. 10.10.1.0/24; Azure reserves 5 addresses per subnet)','Region matching the workload'],
 arch='flowchart TD\n VN[VNet 10.10.0.0/16] --> SN[Subnet 10.10.1.0/24] --> NSG[NSG] --> NIC[NIC and VM]',
 nav=['Virtual networks','Create'],
 st=['<b>Basics</b>: Subscription, Resource group, Name, Region.','<b>IP addresses</b>: set IPv4 address space; add a subnet with name and range.','<b>Review + create</b>, then <b>Create</b>.','Open <b>Network security groups</b> → <b>Create</b>; set Resource group, Name, Region.','NSG → <b>Settings</b> → <b>Inbound security rules</b> → <b>Add</b>: source, destination, service, port, protocol, action, priority, name.','NSG → <b>Settings</b> → <b>Subnets</b> → <b>Associate</b> → choose the VNet and subnet.'],
 v=['VNet → Subnets lists the subnet with NSG attached.','Network Watcher → IP flow verify confirms allow or deny.'],
 rb=['Disassociate the NSG, then delete the NSG, subnet and VNet (no connected devices allowed).'],
 ts=['Address space overlap => peering and VPN will fail; re-plan CIDR.','Traffic blocked => lowest priority number wins; check effective security rules on the NIC.','Cannot delete subnet => remove attached NICs, endpoints or delegations first.'],
 d=['https://learn.microsoft.com/en-us/azure/virtual-network/quick-create-portal','https://learn.microsoft.com/en-us/azure/virtual-network/manage-network-security-group']),
dict(id='alert',cat='Monitoring',t='Create a Metric Alert with an Action Group',p='Notify the right people when a resource metric crosses a threshold.',c=['Alert rule','Action group'],
 pre=['Monitoring Contributor on the scope','Target resource (e.g. a VM)','Threshold, severity and recipients agreed'],
 arch='flowchart TD\n R[Resource metric] --> AR[Alert rule] --> AG[Action group] --> N[Email, SMS, webhook, ITSM]',
 nav=['Monitor','Alerts','Create','Alert rule'],
 st=['<b>Scope</b>: select the resource.','<b>Condition</b>: choose a signal (e.g. Percentage CPU), threshold Static, aggregation Average, operator Greater than, value 80, check every 5 minutes.','<b>Actions</b>: <b>Select action groups</b> or <b>Create action group</b> and add Email/SMS/push/voice notifications.','<b>Details</b>: severity, alert rule name, region.','<b>Review + create</b>, then <b>Create</b>.'],
 v=['Monitor → Alerts → Alert rules lists the rule as Enabled.','Use Test action group to confirm delivery.'],
 rb=['Alert rules → select the rule → Disable or Delete.'],
 ts=['No notification => check action group status and spam filters.','Alert never fires => verify metric, aggregation and lookback window.','Too noisy => raise threshold or use dynamic thresholds.'],
 d=['https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-create-metric-alert-rule']),
dict(id='bkp',cat='Backup & DR',t='Create a Recovery Services Vault and Back Up a VM',p='Protect a VM with a policy-driven backup stored in a vault.',c=['Recovery Services vault','Backup policy','Protected item'],
 pre=['Vault in the same region as the VM','Contributor on the resource group','RPO and retention requirements','Decide vault redundancy (LRS, ZRS, GRS) before first backup'],
 arch='flowchart TD\n VM[VM] --> BP[Backup policy] --> V[Recovery Services vault] --> RP[Recovery points]',
 nav=['Recovery Services vaults','Create'],
 st=['<b>Basics</b>: Subscription, Resource group, Vault name, Region. <b>Review + create</b>, then <b>Create</b>.','Open the vault → <b>Properties</b> → Backup Configuration; set storage redundancy before protecting anything.','Open the vault → <b>Backup</b>; Workload in Azure, backup type Virtual machine.','Select or create a <b>Backup policy</b> (schedule and retention).','<b>Add</b> the VMs, then <b>Enable backup</b>.','Vault → <b>Backup items</b> → the VM → <b>Backup now</b> for the first recovery point.'],
 v=['Backup items shows the VM with a recent recovery point.','Backup jobs shows Completed.'],
 rb=['Stop backup and retain or delete data; soft delete keeps deleted items for 14 days by default.'],
 ts=['VM not listed => it must be in the vault region.','Backup failed => check VM agent and Backup jobs error code.','Cannot delete vault => stop protection and remove all backup items first.'],
 d=['https://learn.microsoft.com/en-us/azure/backup/backup-create-recovery-services-vault','https://learn.microsoft.com/en-us/azure/backup/quick-backup-vm-portal']),
dict(id='bud',cat='Cost',t='Create a Cost Budget with Alerts',p='Track spend against a limit and warn owners before it is exceeded.',c=['Budget','Alert conditions'],
 pre=['Cost Management Contributor (or equivalent) at the scope','Monthly amount','Recipients or an action group'],
 arch='flowchart TD\n S[Scope] --> B[Budget] --> A[Alert at % of budget] --> M[Email or action group]',
 nav=['Cost Management + Billing','Cost Management','Budgets','Add'],
 st=['Select the <b>Scope</b>.','Enter budget <b>Name</b>, <b>Reset period</b> (Monthly), creation and expiration dates, and <b>Amount</b>.','Select <b>Next</b>; under <b>Alert conditions</b> choose type (Actual or Forecasted), % of budget, and recipients or action group.','Select <b>Create</b>.'],
 v=['Budgets lists the budget with current spend against the limit.'],
 rb=['Budgets → select the budget → Delete.'],
 ts=['No alert email => confirm recipient addresses and that spend has crossed the threshold.','Spend not shown => cost data can lag up to 24 hours.','Cannot create => check Cost Management role at this scope.'],
 d=['https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets']),
]
CAT="""Virtual machines|Compute|7|vm
VM scale sets|Compute|7
App Services|Compute|7
Function App|Compute|7
Kubernetes services (AKS)|Compute|7
Container instances|Compute|7
Virtual networks|Networking|5|net
Network security groups|Networking|5|net
Network interfaces|Networking|5
Application security groups|Networking|5
Route tables|Networking|5
Private DNS zones|Networking|5
Virtual network gateways (VPN)|Networking|5
ExpressRoute circuits|Networking|5
NAT gateways|Networking|5
Firewalls|Networking|5
Bastions|Networking|5
Private endpoints|Networking|5
Load balancers|Networking|5
Application gateways|Networking|5
Traffic Manager profiles|Networking|5
Front Door and CDN profiles|Networking|5
Storage accounts|Storage|6|st
Disks (managed disks)|Storage|6
Microsoft Entra ID|Identity|4
App registrations|Identity|4
Enterprise applications|Identity|4
Managed Identities|Identity|4
Conditional Access|Identity|4
Privileged Identity Management|Identity|4
Access control (IAM)|Identity|3|rbac
Policy|Governance|3
Management groups|Governance|2
Subscriptions|Governance|2
Resource groups|Governance|2|rg
Microsoft Defender for Cloud|Security|8
Key vaults|Security|8
DDoS protection plans|Security|8
Monitor|Monitoring|9|alert
Log Analytics workspaces|Monitoring|9
Application Insights|Monitoring|9
Recovery Services vaults|Backup & DR|10|bkp
Site Recovery|Backup & DR|10
Cost Management|Cost|11|bud
Advisor|Cost|11
Reservations|Cost|11
Terraform (code, not a portal service)|IaC|12"""
QR=[('Hierarchy','Tenant → Management group → Subscription → Resource group → Resource'),('Redundancy','LRS 3 copies in one datacenter; ZRS across zones; GRS to paired region; GZRS zones + paired region; RA- adds read access'),('RBAC vs Policy','RBAC controls who can act; Policy controls what can be deployed'),('Policy effects','Deny, Audit, Append, Modify, DeployIfNotExists, AuditIfNotExists, Disabled'),('Control vs data plane','Control plane = ARM management operations; data plane = operations on the resource contents'),('Subnet sizing','Azure reserves 5 addresses per subnet; /24 gives 251 usable'),('RPO and RTO','RPO = tolerable data loss; RTO = tolerable downtime'),('NSG priority','Lower number is evaluated first; first match wins'),('Shared responsibility','Customer always owns data, identities and endpoints')]

def sop_html(s):
    li=lambda a:''.join(f'<li>{x}</li>' for x in a)
    nav=''.join(f'<span>{x}</span>' for x in s['nav'])
    ts=''.join('<tr><td>%s</td><td>%s</td></tr>'%tuple(x.split(' => ')) for x in s['ts'])
    d=' '.join(f'<a href="{u}" target="_blank" rel="noopener">{u.split("/")[-1]}</a>' for u in s['d'])
    return f'''<article class="sop" id="sop-{s['id']}"><h2>SOP: {s['t']}</h2><p class="meta">{s['cat']}</p>
<h3>Purpose</h3><p>{s['p']}</p><h3>What you will create</h3><ul>{li(s['c'])}</ul><h3>Prerequisites</h3><ul>{li(s['pre'])}</ul>
<h3>Architecture</h3><pre class="mermaid">{E(s['arch'])}</pre><h3>Azure Portal navigation</h3><div class="crumb">{nav}</div>
<h3>Procedure</h3><ol class="steps">{li(s['st'])}</ol><h3>Validation</h3><ul>{li(s['v'])}</ul><h3>Rollback</h3><ul>{li(s['rb'])}</ul>
<h3>Troubleshooting</h3><div class="tw"><table><tr><th>Symptom</th><th>Check</th></tr>{ts}</table></div><h3>Official documentation</h3><p>{d}</p></article>'''
exec(open(os.path.join(BASE,'content','sops_core.py'),encoding='utf8').read())
exec(open(os.path.join(BASE,'content','sops_identity_networking.py'),encoding='utf8').read())
exec(open(os.path.join(BASE,'content','sops_storage_compute_monitoring_dr_security_cost.py'),encoding='utf8').read())
exec(open(os.path.join(BASE,'content','sops_more.py'),encoding='utf8').read())
exec(open(os.path.join(BASE,'content','sops_custom.py'),encoding='utf8').read())
exec(open(os.path.join(BASE,'content','sop_enrichment.py'),encoding='utf8').read())
exec(open(os.path.join(BASE,'content','sop_sections.py'),encoding='utf8').read())
exec(open(os.path.join(BASE,'content','screenshots.py'),encoding='utf8').read())
exec(open(os.path.join(BASE,'content','navigation.py'),encoding='utf8').read())
sops=''.join(sop_html(s) for s in SOPS)
sopchips=''.join(f'<a href="#sops" data-t="sop-{s["id"]}">{s["t"]}</a>' for s in SOPS)
sopid={s['id']:s for s in SOPS}
pn={p['n']:p for p in parts}
rows=''
for l in CAT.split('\n'):
    a=l.split('|'); n,c,pt=a[0],a[1],int(a[2]); sp=sopid.get(a[3]) if len(a)>3 else None
    sl=f'<a href="#sop-{sp["id"]}">SOP</a>' if sp else '–'
    rows+=f'<tr data-c="{c}"><td>{n}</td><td>{c}</td><td><a href="#p{pt:02d}">Part {pt}</a></td><td>{sl}</td></tr>'
cats=sorted({l.split('|')[1] for l in CAT.split('\n')})
ts_html=''.join(f'<h3>{s["t"]}</h3><div class="tw"><table><tr><th>Symptom</th><th>Check</th></tr>'+''.join('<tr><td>%s</td><td>%s</td></tr>'%tuple(x.split(' => ')) for x in s['ts'])+'</table></div>' for s in SOPS)
exec(open(os.path.join(BASE,'content','troubleshooting.py'),encoding='utf8').read())
exec(open(os.path.join(BASE,'content','interview.py'),encoding='utf8').read())
exec(open(os.path.join(BASE,'content','services.py'),encoding='utf8').read())
qr=''.join(f'<tr><td>{a}</td><td>{E(b)}</td></tr>' for a,b in QR)
nav_parts=''.join(f'<a href="#{p["p"]}" data-v="{p["p"]}">{p["n"]}. {E(p["short"])}</a>' for p in parts)
arts=''.join(f'<section class="view" id="v-{p["p"]}" data-part="{p["n"]}">{p["body"]}<div class="pager" data-i="{i}"></div></section>' for i,p in enumerate(parts))
meta=json.dumps(dict(parts=[[p['p'],p['short']] for p in parts],sops=len(SOPS),svc=len(CAT.split('\n')),topics=sum(p['h2'] for p in parts)))
T=open(os.path.join(BASE,'template.html'),encoding='utf8').read()
out=(T.replace('%%NAVPARTS%%',nav_parts).replace('%%ARTS%%',arts).replace('%%SOPS%%',sops).replace('%%SOPCHIPS%%',sopchips)
 .replace('%%ROWS%%',rows).replace('%%CATOPTS%%',''.join(f'<option>{c}</option>' for c in cats)).replace('%%TS%%',ts_html).replace('%%QR%%',qr).replace('%%META%%',meta).replace('%%XQ%%',xq).replace('%%TF%%',tf).replace('%%DOMS%%',json.dumps([[c,len(_g[c]),_slug(c)] for c in ORD])).replace('%%SOPTREE%%',soptree).replace('%%ARCH%%',arch).replace('%%SVC%%',svc).replace('%%CMP%%',cmp).replace('%%READY%%',ready))
# MERMAID-FIX: readable theme and spacing for every diagram, and real line breaks for literal \n in labels
_INIT='%%{init: {"theme":"base","themeVariables":{"background":"#ffffff","primaryColor":"#eff6ff","primaryTextColor":"#0f172a","primaryBorderColor":"#2563eb","secondaryColor":"#f1f5f9","secondaryTextColor":"#0f172a","tertiaryColor":"#f8fafc","tertiaryTextColor":"#0f172a","lineColor":"#475569","textColor":"#0f172a","edgeLabelBackground":"#f8fafc","clusterBkg":"#f8fafc","clusterBorder":"#94a3b8","nodeBorder":"#2563eb","mainBkg":"#eff6ff","fontSize":"15px"},"flowchart":{"nodeSpacing":50,"rankSpacing":60,"padding":16,"htmlLabels":true,"useMaxWidth":false,"curve":"basis","subGraphTitleMargin":{"top":10,"bottom":34}}}}%%\n'
out=re.sub(r'(<pre class="mermaid">)(.*?)(</pre>)',lambda m:m.group(1)+_INIT+m.group(2).replace('\\n','&lt;br/&gt;')+m.group(3),out,flags=re.S)
# MINIMAL: replace emoji icons in generated UI chrome with plain labels and CSS dots
for _a,_c in (('<span class="lv">🟢 ','<span class="lv"><i class="dot g"></i>'),('<span class="lv">🟡 ','<span class="lv"><i class="dot y"></i>'),('<span class="lv">🔴 ','<span class="lv"><i class="dot r"></i>'),('<b>💡 ','<b>'),('<b>⚠️ ','<b>'),('<b>💰 ','<b>'),('>🔐 ','>'),('>🏭 ','>'),('>🛠 ','>'),('>⚠️ ','>'),('<p>🟢 ','<p><i class="dot g"></i>'),('<p>🟡 ','<p><i class="dot y"></i>'),('<p>🔴 ','<p><i class="dot r"></i>')):
    out=out.replace(_a,_c)
if LOCAL:
    out=out.replace('</body>','<script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.0/dist/mermaid.min.js"></script><script>if(window.mermaid){mermaid.initialize({startOnLoad:false,securityLevel:"loose"});function rd(){var ns=[].slice.call(document.querySelectorAll(".view.on pre.mermaid:not([data-processed])"));if(ns.length)mermaid.run({nodes:ns}).catch(function(){})}rd();window.addEventListener("hashchange",function(){setTimeout(rd,60)})}</script></body>')
os.makedirs(os.path.join(BASE,'dist'),exist_ok=True)
open(os.path.join(BASE,'dist','index.html'),'w',encoding='utf8').write(out)
print(len(out),meta)
