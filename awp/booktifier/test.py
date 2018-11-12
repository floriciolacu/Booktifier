import numpy as np
from sklearn.svm import SVC

X = np.array([[-1, -1], [-2, -1], [1, 1], [2, 1]])
y = np.array(["ceva", "ceva", "altceva", "altceva"])

np.save('Xfile', X)
np.save('yfile', y)

clf = SVC()
clf.fit(X, y)

def test():
	return 'ceva'

def pred():
	X1 = np.load('Xfile.npy')
	y1 = np.load('yfile.npy')
	res = clf.predict([[-0.8, -1]])
	return res[0]

print(pred())
print(test())