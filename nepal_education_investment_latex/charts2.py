import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
BLUE,ORANGE,AQUA,YELLOW,MAG,GREEN,VIOLET='#2a78d6','#eb6834','#1baf7a','#eda100','#e87ba4','#008300','#6250d6'
INK,INK2,MUTED,GRID,AXIS='#0b0b0b','#52514e','#898781','#e1e0d9','#c3c2b7'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.edgecolor':AXIS,'axes.labelcolor':INK2,
 'xtick.color':MUTED,'ytick.color':MUTED,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,
 'axes.grid':True,'grid.color':GRID,'grid.linewidth':0.6,'axes.axisbelow':True,'ytick.left':False,'legend.frameon':False,'pdf.fonttype':42})

# ---- Fig 5: three cuts of the FY 2026/27 education & sports budget (Rs 218.30 bn) ----
cuts=[
 ('By sub-sector',[('School education',151.70,BLUE),('Management',33.12,ORANGE),('Higher education',24.10,AQUA),('TVET',5.59,YELLOW),('Sports',3.80,MAG)]),
 ('By tier of government',[('Local governments (conditional grants)',150.79,BLUE),('Federal',62.90,ORANGE),('Provincial',4.62,AQUA)]),
 ('By economic nature',[('Salaries and pensions',150.59,BLUE),('Everything else (programmes, grants, capital)',67.71,ORANGE)]),
]
fig,ax=plt.subplots(figsize=(6.6,3.6))
for i,(name,parts) in enumerate(cuts):
    left=0; y=2-i
    for lab,v,c in parts:
        ax.barh(y,v,left=left,color=c,height=0.5,edgecolor='white',linewidth=1.5)
        if v>12: ax.text(left+v/2,y,f"{v:.1f}",ha='center',va='center',fontsize=7,color='white')
        left+=v
    key=' \u00b7 '.join(f"{lab} {v:.1f} bn ({v/218.30*100:.1f}%)" for lab,v,c in parts)
    ax.text(0,y-0.42,key,fontsize=6.2,color=INK2,va='top')
ax.set_yticks([2,1,0]); ax.set_yticklabels([c[0] for c in cuts],fontsize=8); ax.grid(axis='y',visible=False); ax.tick_params(axis='y',length=0)
ax.set_xlim(0,218.3); ax.set_ylim(-0.75,2.45); ax.set_xlabel('Rs billion (FY 2026/27 education and sports budget = Rs 218.30 bn)')
ax.set_title('Three cuts of the FY 2026/27 education and sports budget',loc='left',fontsize=9,color=INK)
fig.savefig('fig_composition.pdf',bbox_inches='tight'); plt.close()

# ---- Fig 6: identified programme lines, FY 2024/25 - 2026/27 ----
items=[('Teacher pensions (federal)',[19.00,19.00,26.50]),('Physical infrastructure (school)',[2.50,2.72,10.45]),('Midday meals',[8.39,10.19,9.54]),
       ('Scholarships (targeted)',[0.60,2.44,8.60]),('Teacher training / mentoring',[None,None,3.20]),('Free textbooks',[3.81,None,None]),
       ('ECED facilitator & school staff grants',[None,10.16,None]),('President Educational Reform Prog.',[0.88,2.72,None]),('Sanitary pads',[None,1.29,None]),('Smart boards (secondary schools)',[None,None,1.07])]
fig,ax=plt.subplots(figsize=(6.6,4.0))
import numpy as np
n=len(items); y=np.arange(n)[::-1]; h=0.26; cols=[AQUA,ORANGE,BLUE]; yrs=['FY 2024/25','FY 2025/26','FY 2026/27']
for j in range(3):
    vals=[it[1][j] for it in items]
    for yy,v in zip(y,vals):
        if v is None: ax.text(0.3,yy+(1-j)*h,'n/p',va='center',fontsize=5.5,color=MUTED)
        else:
            ax.barh(yy+(1-j)*h,v,height=h-0.03,color=cols[j],label=yrs[j] if yy==y[0] else None)
            ax.text(v+0.3,yy+(1-j)*h,f"{v:.2f}",va='center',fontsize=6.3,color=INK)
ax.set_yticks(y); ax.set_yticklabels([it[0] for it in items],fontsize=7.5); ax.grid(axis='y',visible=False); ax.tick_params(axis='y',length=0)
ax.set_xlim(0,30); ax.set_xlabel('Rs billion, initial allocation (n/p = not published / not found for that year)')
ax.legend(loc='lower right',fontsize=7)
ax.set_title('Identified non-salary and pension lines in the education budget',loc='left',fontsize=9,color=INK)
fig.savefig('fig_programmes.pdf',bbox_inches='tight'); plt.close()

# ---- Fig 7: international comparators, % of GDP per capita ----
rows=[('World (2013)',15.56,20.08),('Bhutan (2014/15)',12.85,29.43),('India (2013)',9.79,16.85),('Pakistan (2015)',8.10,16.02),('South Asia (2015/16)',9.90,11.98),
      ('Nepal (2015, WDI)',12.36,10.45),('Bangladesh (2016)',None,9.88),('Sri Lanka (2018)',7.92,7.67),('Vietnam (2013)',21.14,None),('Maldives (2016)',16.08,None)]
fig,ax=plt.subplots(figsize=(6.6,3.6))
n=len(rows); y=np.arange(n)[::-1]; h=0.36
for yy,(name,p,s) in zip(y,rows):
    if p is not None: ax.barh(yy+h/2,p,height=h-0.03,color=BLUE,label='Primary' if yy==y[0] else None); ax.text(p+0.3,yy+h/2,f"{p:.1f}",va='center',fontsize=6.5,color=INK)
    else: ax.text(0.3,yy+h/2,'n/a',va='center',fontsize=6,color=MUTED)
    if s is not None: ax.barh(yy-h/2,s,height=h-0.03,color=ORANGE,label='Secondary' if yy==y[0] else None); ax.text(s+0.3,yy-h/2,f"{s:.1f}",va='center',fontsize=6.5,color=INK)
    else: ax.text(0.3,yy-h/2,'n/a',va='center',fontsize=6,color=MUTED)
ax.axvline(9.7,color=AQUA,lw=1.2,ls='--'); ax.text(9.9,y[0]+0.75,'Nepal FY 2026/27, school allocation ÷ all students = 9.7%',fontsize=6.5,color=AQUA,va='center')
ax.axvline(15.5,color=VIOLET,lw=1.2,ls='--'); ax.text(15.7,y[-1]-0.55,'Nepal FY 2026/27, school allocation ÷ community students = 15.5%',fontsize=6.5,color=VIOLET,va='center')
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows],fontsize=7.5); ax.grid(axis='y',visible=False); ax.tick_params(axis='y',length=0)
ax.set_xlim(0,34); ax.set_ylim(-1.1,n); ax.set_xlabel('Government expenditure per student, % of GDP per capita (World Bank WDI / UIS, latest available year)')
ax.legend(loc='center right',bbox_to_anchor=(1,0.55),fontsize=7)
ax.set_title('Per-student government spending: Nepal and comparators',loc='left',fontsize=9,color=INK)
fig.savefig('fig_intl.pdf',bbox_inches='tight'); plt.close()
