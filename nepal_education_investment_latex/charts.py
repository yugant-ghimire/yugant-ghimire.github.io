import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
D=json.load(open('data.json'))
BLUE,ORANGE,AQUA,YELLOW,VIOLET,MAG='#2a78d6','#eb6834','#1baf7a','#eda100','#6250d6','#e87ba4'
INK,INK2,MUTED,GRID,AXIS='#0b0b0b','#52514e','#898781','#e1e0d9','#c3c2b7'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.edgecolor':AXIS,'axes.labelcolor':INK2,
 'xtick.color':MUTED,'ytick.color':MUTED,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,
 'axes.grid':True,'grid.color':GRID,'grid.linewidth':0.6,'axes.axisbelow':True,'ytick.left':False,'legend.frameon':False,
 'pdf.fonttype':42,'figure.dpi':150})
x=list(range(len(D))); labels=[d['fy_ad'][2:] for d in D]  # '08/09'
def style(ax):
    ax.grid(axis='x',visible=False); ax.set_xticks(x); ax.set_xticklabels(labels,rotation=90,fontsize=7)
    ax.tick_params(axis='x',length=0)
fmt=lambda v:f"{v:,.0f}"

# Governments (by PM who presented the budget) -> shading bands
govs=[('Dahal I',0,0),('M.K. Nepal',1,2),('Khanal',3,3),('Bhattarai',4,4),('Regmi',5,5),
      ('Koirala',6,7),('Oli I',8,8),('Dahal II',9,9),('Oli II',10,13),('Deuba',14,14),
      ('Dahal III',15,16),('Oli III',17,17),('Shah',18,18)]
def bands(ax,ytext,fs=6.2):
    for i,(n,a,b) in enumerate(govs):
        if i%2==0: ax.axvspan(a-0.5,b+0.5,color='#f1f0ec',zorder=0,lw=0)
        ax.text((a+b)/2,ytext,n,ha='center',va='top',fontsize=fs,color=INK2,rotation=90)

# ---------- Fig 1: budget share and allocation ----------
fig,(a1,a2)=plt.subplots(2,1,figsize=(6.6,4.6),sharex=True,gridspec_kw={'hspace':0.35})
sh=[float(d['share_pct']) for d in D]
a1.plot(x,sh,color=BLUE,lw=2,marker='o',ms=4,mfc='white',mew=1.5)
for i in [0,2,8,9,18]: a1.annotate(f"{sh[i]:.1f}%",(i,sh[i]),xytext=(0,6),textcoords='offset points',ha='center',fontsize=7,color=INK)
a1.axhline(20,color=ORANGE,lw=1,ls='--'); a1.text(18.4,20.3,'20% commitment',color=ORANGE,fontsize=7,ha='right',va='bottom')
a1.set_ylim(0,23); a1.set_title('Education allocation as a share of the federal budget (%)',loc='left',fontsize=9,color=INK)
edu=[float(d['edu_bn']) for d in D]
a2.bar(x,edu,color=BLUE,width=0.7)
for i in [0,5,10,18]: a2.text(i,edu[i]+4,fmt(edu[i]),ha='center',fontsize=7,color=INK)
a2.set_title('Education allocation, Rs billion (nominal, initial estimate)',loc='left',fontsize=9,color=INK)
style(a2); a2.set_xlabel('Fiscal year (AD)'); a2.set_ylim(0,250)
fig.savefig('fig_budget.pdf',bbox_inches='tight'); plt.close()

# ---------- Fig 2: enrolment ----------
fig,ax=plt.subplots(figsize=(6.6,3.3))
tot=[d['enrol']/1e6 if d['enrol'] else None for d in D]
pub=[d['public']/1e6 if d['public'] else None for d in D]
est=[d['public_est']/1e6 if d['public_est'] else None for d in D]
priv=[(d['enrol']-d['public'])/1e6 if d['public'] and d['enrol'] else None for d in D]
xs=x[:-1]  # FY2026/27 repeats 2025/26 enrolment -> don't plot
ax.plot(xs,tot[:-1],color=BLUE,lw=2,label='All students, grades 1–12')
ax.plot(xs,est[:-1],color=ORANGE,lw=1.6,ls=(0,(3,2)),label='Community schools (estimated, see §4.2)')
ax.plot(xs,pub[:-1],color=ORANGE,lw=2,marker='o',ms=4,mfc='white',mew=1.5,label='Community schools (Flash / Economic Survey)')
ax.plot(xs,priv[:-1],color=AQUA,lw=2,marker='o',ms=4,mfc='white',mew=1.5,label='Institutional (private) schools')
for i,v in [(17,pub[17]),(17,priv[17]),(17,tot[17]),(10,pub[10]),(13,priv[13])]:
    ax.annotate(f"{v:.2f} m",(i,v),xytext=(5,0),textcoords='offset points',fontsize=7,color=INK,va='center')
ax.set_ylim(0,8.5); ax.set_ylabel('Million students'); style(ax); ax.set_xlim(-0.5,17.5); ax.set_xticks(xs); ax.set_xticklabels(labels[:-1],rotation=90,fontsize=7)
ax.set_title('School enrolment (grades 1–12), by school type',loc='left',fontsize=9,color=INK)
ax.legend(loc='lower left',fontsize=7,ncol=2); ax.set_xlabel('School year (AD)')
fig.savefig('fig_enrol.pdf',bbox_inches='tight'); plt.close()

# ---------- Fig 3: per-student trend, nominal and real, with governments ----------
fig,(a1,a2)=plt.subplots(2,1,figsize=(6.6,6.6),sharex=True,gridspec_kw={'hspace':0.3})
pa=[d['per_all']/1e3 for d in D]; pp=[d['per_pub']/1e3 if d['per_pub'] else None for d in D]; pe=[d['per_pub_est']/1e3 if d['per_pub_est'] else None for d in D]
a1.plot(x,pa,color=BLUE,lw=2,marker='o',ms=3.5,mfc='white',mew=1.3,label='Per enrolled student (all schools)')
a1.plot(x,pe,color=ORANGE,lw=1.6,ls=(0,(3,2)),label='Per community-school student (estimated)')
a1.plot(x,pp,color=ORANGE,lw=2,marker='o',ms=3.5,mfc='white',mew=1.3,label='Per community-school student (Flash data)')
for i in [0,10,18]: a1.annotate(fmt(pa[i]*1e3),(i,pa[i]),xytext=(0,-13),textcoords='offset points',ha='center',fontsize=7,color=INK)
for i in [10,18]: a1.annotate(fmt(pp[i]*1e3),(i,pp[i]),xytext=(-14 if i==18 else 0,6),textcoords='offset points',ha='center',fontsize=7,color=INK)
a1.set_ylim(0,66); a1.set_ylabel('Rs thousand per student'); bands(a1,65)
a1.set_title('Education allocation per student — nominal rupees',loc='left',fontsize=9,color=INK)
a1.legend(loc='lower right',fontsize=7)
ra=[d['per_all_real']/1e3 for d in D]; rp=[d['per_pub_real']/1e3 if d['per_pub_real'] else None for d in D]
re_=[d['edu_bn']and (float(d['edu_bn'])*1e9/d['public_est']/d['deflator']/1e3) if d['public_est'] else None for d in D]
a2.plot(x,ra,color=BLUE,lw=2,marker='o',ms=3.5,mfc='white',mew=1.3)
a2.plot(x,re_,color=ORANGE,lw=1.6,ls=(0,(3,2)))
a2.plot(x,rp,color=ORANGE,lw=2,marker='o',ms=3.5,mfc='white',mew=1.3)
for i in [0,8,11,18]: a2.annotate(fmt(ra[i]*1e3),(i,ra[i]),xytext=(0,-11),textcoords='offset points',ha='center',fontsize=7,color=INK)
for i in [10,17]: a2.annotate(fmt(rp[i]*1e3),(i,rp[i]),xytext=(-4,6),textcoords='offset points',ha='center',fontsize=7,color=INK)
a2.set_ylim(0,66); a2.set_ylabel('Rs thousand per student\n(FY 2025/26 prices)'); bands(a2,65); style(a2); a2.set_xlabel('Fiscal year (AD); shaded bands = government that presented the budget')
a2.set_title('Education allocation per student — real terms (CPI-deflated)',loc='left',fontsize=9,color=INK)
fig.savefig('fig_perstudent.pdf',bbox_inches='tight'); plt.close()

# ---------- Fig 4: by government, average real per-student ----------
import statistics
names=[];vals=[];vals_pub=[];fms=[]
for n,a,b in govs:
    names.append(n.replace('\n',' '))
    vals.append(statistics.mean(ra[a:b+1]))
    seq=[(rp[i] if rp[i] is not None else re_[i]) for i in range(a,b+1)]
    vals_pub.append(statistics.mean(seq))
fig,ax=plt.subplots(figsize=(6.6,3.6))
y=list(range(len(names)))[::-1]
ax.barh([v+0.2 for v in y],vals,height=0.38,color=BLUE,label='Per enrolled student (all schools)')
ax.barh([v-0.2 for v in y],vals_pub,height=0.38,color=ORANGE,label='Per community-school student')
for yy,v,w in zip(y,vals,vals_pub):
    ax.text(v+0.5,yy+0.2,fmt(v*1e3),va='center',fontsize=7,color=INK); ax.text(w+0.5,yy-0.2,fmt(w*1e3),va='center',fontsize=7,color=INK)
ax.set_yticks(y); ax.set_yticklabels(names,fontsize=7.5); ax.grid(axis='y',visible=False); ax.tick_params(axis='y',length=0)
ax.set_xlim(0,58); ax.set_xlabel('Rs thousand per student per year, FY 2025/26 prices (average over the budgets each government presented)')
ax.legend(loc='upper right',fontsize=7)
ax.set_title('Real education allocation per student, by government presenting the budget',loc='left',fontsize=9,color=INK)
fig.savefig('fig_bygov.pdf',bbox_inches='tight'); plt.close()
json.dump({'gov':list(zip(names,vals,vals_pub))},open('bygov.json','w'))
print(list(zip(names,[round(v*1e3) for v in vals],[round(v*1e3) for v in vals_pub])))
