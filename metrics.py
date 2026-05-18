def add_csi_metric():
    def csi_score(y, y_pred, **kwargs):
        tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()
        return tp / (tp + fn + fp + 1e-10)
    add_metric(id='csi', name='CSI', score_func=csi_score,
               greater_is_better=True, target='pred')