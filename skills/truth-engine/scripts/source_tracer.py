def trace(source_id,sources):
    by_id={s['source_id']:s for s in sources}
    def walk(i,path):
        if i in path: return [{'path':path+[i],'stop':'CYCLE'}]
        s=by_id.get(i)
        if not s: return [{'path':path+[i],'stop':'MISSING_SOURCE'}]
        path=path+[i]
        if s['kind']=='PRIMARY': return [{'path':path,'stop':'PRIMARY'}]
        refs=s.get('derived_from',[])
        if not refs: return [{'path':path,'stop':'UNRESOLVED_ORIGIN'}]
        return [p for ref in refs for p in walk(ref,path)]
    return walk(source_id,[])
