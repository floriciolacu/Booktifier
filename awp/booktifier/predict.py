import sys
import os
import django
path = os.path.realpath(__file__)
path = path.split('/')
path.pop()
path.pop()
path = '/'.join(path)
sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE']='awp.settings'
django.setup()
from booktifier.models import Book, Author
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import numpy as np
import json
import difflib
from sklearn.svm import SVC
import tempfile
import cv2

def make_dictionary():
	book_list = Book.objects.all()
	author_list = Author.objects.all()

	number_words_books = 0
	number_words_authors = 0

	words_books = []
	words_authors = []

	dictionary = {}

	for book in book_list:
		for word in book.title.split():
			number_words_books = number_words_books + 1

	for author in author_list:
		number_words_authors = number_words_authors + 2

	for book in book_list:
		for word in book.title.split():
			words_books.append(word)

	for author in author_list:
		words_authors.append(author.first_name)
		words_authors.append(author.last_name)


	number_words = number_words_books + number_words_authors

	for key in range(0, number_words_books):
		dictionary[key] = words_books[key]

	for key in range(number_words_books, number_words):
		dictionary[key] = words_authors[key - number_words_books]

	return dictionary

dictionary = make_dictionary()

def get_prediction(file, dict):
	training_data = np.load('TrainingData.npy')
	labels = np.load('Labels.npy')
	clf = SVC()
	clf.fit(training_data, labels)
	val = np.zeros(len(dict), dtype=int)
	img = cv2.imread("media/" + file, cv2.IMREAD_COLOR)
	img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	kernel = np.ones((1, 1), np.uint8)
	img = cv2.dilate(img, kernel, iterations=12)
	img = cv2.erode(img, kernel, iterations=12)
	cv2.imwrite("temp.jpg", img)
	text = pytesseract.image_to_string(Image.open('temp.jpg'), lang = 'ron', config = '--psm 1')
	for word in text.split():
		for key in dict:
			if len(word) <= 4:
				if word.lower() == dict[key].lower():
					val[key] = 1
			else:
				if difflib.SequenceMatcher(None, word.lower(), dict[key].lower()).ratio() > 0.70:
					val[key] = 1

	prediction = clf.predict([val])
	return prediction

file = '001.JPG'
result = get_prediction(file, dictionary)[0]
print(result)