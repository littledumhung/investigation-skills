"""Conservative evidence gates; agent supplies semantic assessment, not probabilities."""
VERDICTS=['TRUE','MOSTLY_TRUE','MIXED','MISLEADING','FALSE','OUTDATED','UNVERIFIED','NOT_CHECKABLE']
def recommend(*,checkable=True,support=False,refutation=False,misleading=False,outdated=False,corrected=False):
    if not checkable: return 'NOT_CHECKABLE'
    if corrected: return 'UNVERIFIED'
    if outdated and support and refutation: return 'OUTDATED'
    if misleading and (support or refutation): return 'MISLEADING'
    if support and refutation: return 'MIXED'
    if refutation: return 'FALSE'
    if support: return 'TRUE'
    return 'UNVERIFIED'
