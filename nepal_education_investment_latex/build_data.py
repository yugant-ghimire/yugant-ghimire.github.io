import csv, json
rows = list(csv.DictReader(open('budget.csv')))
# World Bank (UIS) enrollment: WB year Y <-> school/fiscal year (Y-1)/Y  (verified: WB2023 primary 3,610,603 == Flash 2079 (2022/23))
prm = {2008:4418713,2009:4782313,2010:4900663,2011:4951956,2012:4782885,2013:4576693,2014:4401780,2015:4335355,2016:4135253,2017:3970016,2018:3970016,2019:3970016,2020:3522177,2021:3455710.6,2022:3485293.3,2023:3610603,2024:3519214,2025:3565348}
sec = {2008:2305166,2009:2381225,2010:2694256,2011:2850361,2012:3035958,2013:3111257,2014:3163946,2015:3176320,2016:3277231,2017:3433843,2018:3448803,2019:3463763,2020:3631853,2021:3541369.1,2022:3512976,2023:3695560,2024:3668708}
privprm = {2008:10.25,2009:11.70,2010:13.15,2011:11.88,2012:14.03,2013:15.10,2014:15.40,2015:15.45,2016:15.32,2017:16.57,2018:16.57,2019:16.57,2020:25.38}
cpi = {2008:82.334,2009:91.469,2010:100,2011:109.227,2012:119.560,2013:130.368,2014:141.272,2015:152.389,2016:165.784,2017:170.388,2018:177.897,2019:187.799,2020:197.294,2021:205.436,2022:221.194,2023:236.934,2024:248.034,2025:254.615}
cpi[2026] = cpi[2025]*1.05; cpi[2027]=cpi[2026]*1.05  # assumption: 5% (flagged in report)
# Flash / Economic Survey totals (grades 1-12), community & institutional
flash = {  # end-year -> (total, community, institutional, source)
 2019:(None,5277152,None,'ssdp2020'),      # 2018/19 community only (basic 4,124,478 + secondary 1,152,674)
 2022:(7096134,5258275,1837859,'sesp2022'),
 2023:(7228397,5101025,1989845,'flash2079'),  # religious 137,527 separate
 2024:(7143262,4995466,2147796,'flash2080'),
 2025:(7010808,4642729,2368079,'collegenp2025'),
 2026:(7040825,4383655,2657170,'kp2026es'),
}
schoolproxy = {2022:114.91,2023:121.01,2025:141.36,2026:145.68,2027:151.69}  # Rs bn: LG education conditional grants / 2026-27 school sub-line
out=[]
for r in rows:
    y = int(r['fy_ad'][:4])+1
    edu=float(r['edu_bn'])*1e9
    tot_enr = None; pub=None; pub_est=None; src=None
    if y in flash and flash[y][0]: tot_enr=flash[y][0]; src=flash[y][3]
    elif y in prm and y in sec: tot_enr=prm[y]+sec[y]; src=('wb_interp' if y==2018 else 'wb')
    if y in flash: pub=flash[y][1]
    if y==2027:  # FY2026/27: use latest ES 2082/83 (2025/26) enrollment
        tot_enr=flash[2026][0]; pub=flash[2026][1]; src='kp2026es (2025/26 enrolment)'
    # pre-2019 public estimate: assume private share of secondary = private share of primary (WB)
    if pub is None and y in privprm and tot_enr:
        pub_est = tot_enr*(1-privprm[y]/100)
    if y==2020: pub_est = prm[2020]*(1-25.38/100)+sec[2020]*(1-23.77/100)   # WB 2020 primary & secondary private shares
    if y==2021: pub_est = tot_enr*(1-0.259)   # assume 2021/22 Flash institutional share (25.9%)
    deflator = (cpi[y-1]+cpi[y])/2 / ((cpi[2025]+cpi[2026])/2)   # FY 2025/26 prices
    d=dict(r); d.update(dict(end=y,enrol=tot_enr,enrol_src=src,public=pub,public_est=pub_est,
        per_all = edu/tot_enr if tot_enr else None,
        per_pub = edu/pub if pub else None,
        per_pub_est = edu/pub_est if pub_est else None,
        per_all_real = edu/tot_enr/deflator if tot_enr else None,
        per_pub_real = edu/pub/deflator if pub else None,
        school_proxy_bn = schoolproxy.get(y),
        per_pub_school = schoolproxy[y]*1e9/pub if y in schoolproxy and pub else None,
        deflator=deflator))
    out.append(d)
json.dump(out,open('data.json','w'),indent=1)
for d in out:
    f=lambda v: '-' if v is None else str(round(v))
    print(d['fy_ad'],d['edu_bn'],'enr',f(d['enrol']),'pub',f(d['public']),'est',f(d['public_est']),'| all',f(d['per_all']),'pub',f(d['per_pub']),'pubest',f(d['per_pub_est']),'realall',f(d['per_all_real']),'realpub',f(d['per_pub_real']),'school/pub',f(d['per_pub_school']))
