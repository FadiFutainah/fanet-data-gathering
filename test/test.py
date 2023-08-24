import pandas as pd
import inspect

from src.environment.utils.vector import Vector

data = pd.read_csv('data/input/test_sample_2/' + 'sensors.csv')

print(data.columns[0])


class Bla:
    def __init__(self, x, y, z=2):
        self.z = z
        self.x = x
        self.y = y

    @classmethod
    def create_empty_object(cls) -> object:
        signature = inspect.signature(cls.__init__)
        attrs = list(signature.parameters.keys())[1:]
        print(signature)
        for p in list(signature.parameters.keys())[1:]:
            print(p)
        num_of_params = len(signature.parameters) - 1
        params = 'None,' * num_of_params
        obj = None
        exec(f'obj = {cls.__name__}({params})')
        return obj


# e = Bla.create_empty_object()
# print(type(e))

# import pandas as pd
#
# name = 'Vector'
#
# # Create a DataFrame with sample data
# data = {'Name': [],
#         'Age': []
#         }
# signature = inspect.signature(Vector.__init__)
# attrs = list(signature.parameters.keys())[1:]
# print(signature)
#
# data[] = []
#
# df = pd.DataFrame(data)
#
# # Write the DataFrame to a CSV file
# file_path = f'data/input/test_sample_0/{name}.csv'  # Replace with your desired file path
# df.to_csv(file_path, index=False)
