import numpy as np
# Source: https://docs.scipy.org/doc/numpy-1.13.0/reference/routines.array-manipulation.html
a = np.random.rand(6, 6)
print(a)
print("\n")
a = np.reshape(a, [3,2,6]) #
print(a)
print("\n")
l = []; #
for i in range(0,3):
    array = np.split(a[i], 3, axis=1)
    array_stack = np.stack(array, axis=0)
    l.append(array_stack)
    print(l)
    print("\n")
print(tuple(l))
X_train = np.stack(tuple(l))#
print(np.shape(X_train))
print(X_train)

'''
- Learned: np.reshape populate data by first get the row, then distribute all columns into the new array before moving on to the new row. 
So it goes left to right, top to bottom to distribute elements of old array to reshaped array
'''
