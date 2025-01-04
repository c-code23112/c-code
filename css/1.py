#20
import numpy as np
a=np.ones((3,4)).sum()
print(a)
#22
b=all(np.random.rand(20000)<1)
print(b)
#34
x = np.random.randint(0, 100, (3, 5))
result = np.ceil(np.abs(np.sin(x))).sum()
print(result)
#37
x = np.array([3, 5, 1, 9, 6, 3])
result37 = np.where(x > 5, 1, 0).sum()
print(result37)
