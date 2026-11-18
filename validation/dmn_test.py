import re, itertools, os, sys
from lxml import etree
NS={'d':'https://www.omg.org/spec/DMN/20191111/MODEL/'}
t=etree.parse(sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','models','S08_Credit_Check.dmn'))
def test(expr, v):
    e=expr.strip()
    if e=='-': return True
    m=re.fullmatch(r'([\(\[])\s*([\d.]+)\s*\.\.\s*([\d.]+)\s*([\)\]])',e)
    if m:
        lo,hi=float(m[2]),float(m[3])
        return (v>lo if m[1]=='(' else v>=lo) and (v<hi if m[4]==')' else v<=hi)
    m=re.fullmatch(r'(<=|>=|<|>)\s*([\d.]+)',e)
    if m: return eval(f"{v}{m[1]}{float(m[2])}")
    if e in('true','false'): return v==(e=='true')
    if e.startswith('"'): return v==e.strip('"')
    raise ValueError(e)
def table(did):
    dt=t.find(f".//d:decision[@id='{did}']/d:decisionTable",NS)
    rules=[( [ie.findtext('d:text',namespaces=NS) for ie in r.findall('d:inputEntry',NS)], r.find('d:outputEntry/d:text',NS).text.strip('"')) for r in dt.findall('d:rule',NS)]
    return dt.get('hitPolicy'), rules
def evaluate(did, inputs):
    hp,rules=table(did); hits=[(i+1,o) for i,(ins,o) in enumerate(rules) if all(test(e,v) for e,v in zip(ins,inputs))]
    return hits
# completeness / uniqueness over boundary values
bad=0; n=0
for dpd,yrs in itertools.product([0,3,5,5.5,6,20,20.5,21,60],[0,2.9,3,10]):
    h=evaluate('d_risk',[dpd,yrs]); n+=1
    if len(h)!=1: bad+=1; print('risk', dpd,yrs,h)
for risk,over,ins,disp in itertools.product(['Low','Medium','High'],[0,10,10.5,11,20,20.5,21,80],[True,False],[True,False]):
    h=evaluate('d_rel',[risk,over,ins,disp]); n+=1
    if len(h)!=1: bad+=1; print('release', risk,over,ins,disp,h)
print(f"{n} boundary cases, {bad} not matched exactly once (UNIQUE hit policy)")
# expected cases (Section 8.6 style)
cases=[([2,8],'Low'),([12,1],'Medium'),([30,9],'High'),([4,1],'Medium')]
for i,e in cases: print('risk',i,evaluate('d_risk',i)[0][1],'expected',e)
cases=[(['Low',15,False,False],'Release'),(['Low',30,True,False],'Release with notice to Sales'),(['Low',30,True,True],'Review by analyst'),(['Medium',8,False,False],'Release with notice to Sales'),(['High',0,True,False],'Review by analyst')]
for i,e in cases:
    r=evaluate('d_rel',i)[0]; print('release',i,'rule',r[0],r[1],'OK' if r[1]==e else 'FAIL')
