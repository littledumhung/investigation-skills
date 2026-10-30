"""Structured metadata gates, not automated full-paper methods review."""
def review_status(publication_type,correction_status,full_text_available):
    if correction_status=='RETRACTED': status='RETRACTED_DO_NOT_USE_AS_SUPPORT'
    elif correction_status=='CORRECTED': status='RECHECK_CORRECTED_VERSION'
    elif publication_type=='PREPRINT': status='NOT_CONFIRMED_PEER_REVIEWED'
    else: status='PEER_REVIEW_STATUS_REQUIRES_VERIFICATION'
    return {'status':status,'methods_review':'AGENT_REVIEW_REQUIRED' if full_text_available else 'FULL_REVIEW_NOT_POSSIBLE','causality':'REQUIRES_DESIGN_AND_CONFOUNDING_ASSESSMENT'}
