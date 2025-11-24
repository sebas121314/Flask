import pickle, traceback
print('loading...')
try:
    with open('archivos/modelo_regresion_logistica.pkl','rb') as f:
        model = pickle.load(f)
    print('loaded', type(model))
    print('repr', model)
    import sklearn
    from sklearn.pipeline import Pipeline
    print('is pipeline', isinstance(model, Pipeline))
    if isinstance(model, Pipeline):
        print('steps', model.named_steps)
    if hasattr(model, 'feature_names_in_'):
        print('feature_names', model.feature_names_in_)
    if hasattr(model, 'classes_'):
        print('classes', model.classes_)
except Exception as e:
    print('ERROR')
    traceback.print_exc()
