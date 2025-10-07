# Placeholder for evaluation metrics
def compute_f1(y_true, y_pred):
    '''Return simple F1 placeholder; replace with seqeval later.'''
    from sklearn.metrics import f1_score
    return f1_score(y_true, y_pred, average='micro')
