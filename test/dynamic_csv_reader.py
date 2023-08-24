import inspect

import pandas as pd


def read_csv_table(self, filename, class_name, object_kwargs):
    if len(filename) <= 4 or filename[-4:] != '.csv':
        filename += '.csv'
    df = pd.read_csv(self.input_dir + filename)
    signature = inspect.signature(class_name.__init__)
    params = list(signature.parameters.items())[1:]
    obj_list = []
    for index, row in df.iterrows():
        kwargs = {}
        for param_name, param in params:
            type_hint = param.annotation
            if type_hint is not int and type_hint is not str and type_hint is not float:
                continue
            if param_name == 'id':
                kwargs[param_name] = index
            else:
                kwargs[param_name] = row.get(param_name)
        kwargs = dict(Counter(kwargs) + Counter(object_kwargs))
        obj = class_name(*kwargs)
        obj_list.append(obj)
    return obj_list
