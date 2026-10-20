import json
D=json.load(open('data.json')); G=json.load(open('bygov.json'))['gov']
cite={'nce2020':'nce2020,fcgo','unicef2020':'unicef2020','kp2019':'kp2019,unicef2020','kp2020':'kp2020','nce2025':'nce2025,unicef2022',
      'mof2023':'mof2023,nce2025','unicef2024':'unicef2024,edusanjal2024','kp2025':'kp2025,nce2025','radionepal2026':'radionepal2026,ican2026'}
esrc={'wb':'wb_enrol','wb_interp':'wb_enrol','ssdp2020':'ssdp2020,wb_enrol','sesp2022':'sesp2022','flash2079':'flash2079','flash2080':'flash2080',
      'collegenp2025':'collegenp2025','kp2026es':'kp2026es','kp2026es (2025/26 enrolment)':'kp2026es'}
n=lambda v,d=0: '--' if v is None else f"{v:,.{d}f}"
# Table A: budget
L=[]
for d in D:
    L.append(f"{d['fy_ad']} & {d['fy_bs']} & {float(d['total_bn']):,.2f} & {float(d['edu_bn']):,.2f} & {float(d['share_pct']):.2f} & \\cite{{{cite[d['bibkey']]}}} \\\\")
open('tab_budget.tex','w').write('\n'.join(L))
# Table B: enrolment
L=[]
for d in D[:-1]:
    flag = '$^\\dagger$' if d['enrol_src']=='wb_interp' else ''
    pub = n(d['public']) if d['public'] else (n(d['public_est'])+'$^\\ast$' if d['public_est'] else '--')
    priv = n(d['enrol']-d['public']) if d['public'] and d['enrol'] else '--'
    L.append(f"{d['fy_ad']} & {n(d['enrol'])}{flag} & {pub} & {priv} & \\cite{{{esrc[d['enrol_src']]}}} \\\\")
open('tab_enrol.tex','w').write('\n'.join(L))
# Table C: governments and per-student
L=[]
for d in D:
    pp = n(d['per_pub']) if d['per_pub'] else (n(d['per_pub_est'])+'$^\\ast$' if d['per_pub_est'] else '--')
    rp = n(d['per_pub_real']) if d['per_pub_real'] else (n(float(d['edu_bn'])*1e9/d['public_est']/d['deflator'])+'$^\\ast$' if d['public_est'] else '--')
    L.append(f"{d['fy_ad']} & {d['pm']} & {d['fm']} & {d['party']} & {n(d['per_all'])} & {pp} & {n(d['per_all_real'])} & {rp} \\\\")
open('tab_gov.tex','w').write('\n'.join(L))
# Table D: by government
party={'Dahal I':'CPN (Maoist)','M.K. Nepal':'CPN-UML','Khanal':'CPN-UML','Bhattarai':'UCPN (Maoist)','Regmi':'Non-party (election govt.)','Koirala':'Nepali Congress','Oli I':'CPN-UML','Dahal II':'CPN (Maoist Centre)','Oli II':'NCP / CPN-UML','Deuba':'Nepali Congress','Dahal III':'CPN (Maoist Centre)','Oli III':'CPN-UML','Shah':'RSP'}
fy={'Dahal I':'2008/09','M.K. Nepal':'2009/10--2010/11','Khanal':'2011/12','Bhattarai':'2012/13','Regmi':'2013/14','Koirala':'2014/15--2015/16','Oli I':'2016/17','Dahal II':'2017/18','Oli II':'2018/19--2021/22','Deuba':'2022/23','Dahal III':'2023/24--2024/25','Oli III':'2025/26','Shah':'2026/27'}
L=[]
for name,v,w in G:
    L.append(f"{name} & {party[name]} & {fy[name]} & {v*1e3:,.0f} & {w*1e3:,.0f} \\\\")
open('tab_bygov.tex','w').write('\n'.join(L))
# headline numbers
d=D[-1]
print('FY26/27 school/pub', 151.69e9/d['public'], 'school ex infra/pub', 141.24e9/d['public'], 'edu/pub', d['per_pub'], 'edu/all', d['per_all'], 'school/all',151.69e9/d['enrol'])
print('2018/19 pub', D[10]['per_pub'], 'real', D[10]['per_pub_real'])
print('2021/22 real pub', D[13]['per_pub_real'], '2025/26', D[17]['per_pub_real'])
