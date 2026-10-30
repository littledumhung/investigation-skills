"""Decimal computations with input provenance and explicit comparability."""
from decimal import Decimal, localcontext, ROUND_HALF_UP
from statistics import median
D=lambda x: Decimal(str(x))
def calculate(operation,values,*,sources,unit,assumptions=None,round_digits=4):
    if not sources or not unit: raise ValueError('Sources and unit required')
    if not 0 <= round_digits <= 12: raise ValueError('round_digits must be 0..12')
    v=[D(x) for x in values]
    if not v or any(not x.is_finite() for x in v): raise ValueError('Finite input required')
    with localcontext() as ctx:
        ctx.prec=40
        if operation=='percent_change':
            if len(v)!=2 or v[0]<=0: raise ValueError('Positive baseline and two values required')
            result=(v[1]-v[0])/v[0]*100; formula='(new-old)/old*100'
        elif operation=='cagr':
            if len(v)!=3 or min(v)<=0: raise ValueError('Positive start, end, years required')
            result=((v[1]/v[0])**(1/v[2])-1)*100; formula='((end/start)^(1/years)-1)*100'
        elif operation=='mean': result=sum(v)/len(v); formula='sum(values)/n'
        elif operation=='median': result=median(v); formula='median(values)'
        elif operation=='proportion':
            if len(v)!=2 or v[1]<=0 or not 0<=v[0]<=v[1]: raise ValueError('Invalid numerator/denominator')
            result=v[0]/v[1]; formula='numerator/denominator'
        elif operation in ('risk_ratio','risk_difference'):
            if len(v)!=2 or any(not 0<=x<=1 for x in v): raise ValueError('Two probabilities 0..1 required')
            if operation=='risk_ratio': result=v[0]/v[1]; formula='risk_exposed/risk_control'
            else: result=v[0]-v[1]; formula='risk_exposed-risk_control'
        else: raise ValueError('Unknown operation')
        rounded=result.quantize(D(1).scaleb(-round_digits),rounding=ROUND_HALF_UP)
    return {'operation':operation,'values':[str(x) for x in v],'sources':sources,'unit':unit,'formula':formula,'result':str(rounded),'rounding':'ROUND_HALF_UP','round_digits':round_digits,'assumptions':assumptions or []}
def compare_context(a,b):
    fields=('currency','unit','period_length','fiscal_basis','population','scope','price_basis')
    return {k:('UNKNOWN' if a.get(k) is None or b.get(k) is None else 'MATCH' if a[k]==b[k] else 'MISMATCH') for k in fields}
