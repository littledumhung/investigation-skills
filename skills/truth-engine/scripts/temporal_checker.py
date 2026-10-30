from datetime import date, datetime, timezone
FIELDS=('event_at','spoken_at','collected_at','published_at','updated_at','accessed_at','effective_from','effective_until')
def normalize(value):
    if value is None: return None
    if len(value)==10: return date.fromisoformat(value).isoformat()
    d=datetime.fromisoformat(value.replace('Z','+00:00'))
    if d.tzinfo is None: raise ValueError('Timestamp requires timezone')
    return d.astimezone(timezone.utc).isoformat()
def temporal_status(source,as_of):
    cutoff=date.fromisoformat(as_of)
    for k in FIELDS:
        if source.get(k): normalize(source[k])
    if source.get('published_at') and date.fromisoformat(source['published_at'][:10])>cutoff: return 'POST_CUTOFF'
    if source.get('effective_from') and date.fromisoformat(source['effective_from'][:10])>cutoff: return 'NOT_YET_EFFECTIVE'
    if source.get('effective_until') and date.fromisoformat(source['effective_until'][:10])<=cutoff: return 'EXPIRED'
    return 'IN_SCOPE' if source.get('published_at') else 'UNKNOWN_DATE'
