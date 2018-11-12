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

def write_to_txt():
	with open('words.txt', 'w') as f:
	    for key, value in dictionary.items():
	        f.write('%s\n' % (value.upper()))

def get_training_data(dict):
	training_data = []
	labels = []

	directory_in_str = "/home/tgr2/Booktifier/awp/training_photos"

	directory = os.fsencode(directory_in_str)

	for file in os.listdir(directory):
		filename = os.fsdecode(file)
		if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg") or filename.lower().endswith(".png") or filename.lower().endswith(".tiff") or filename.lower().endswith(".bmp"): 
			if filename != "temp.jpg":
				val = np.zeros(len(dict), dtype=int)
				img = cv2.imread("training_photos/" + filename, cv2.IMREAD_COLOR)
				img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
				#ret,th = cv2.threshold(img,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
				#image, contours, hierarchy = cv2.findContours(th,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
				#img = cv2.drawContours(img, contours, -1, (0,255,0), 3)
				#img = cv2.bitwise_not(img)
				kernel = np.ones((1, 1), np.uint8)
				img = cv2.dilate(img, kernel, iterations=12)
				img = cv2.erode(img, kernel, iterations=12)
				cv2.imwrite("temp.jpg", img)
				text = pytesseract.image_to_string(Image.open('temp.jpg'), lang = 'ron', config = '--psm 1 --user-words /home/tgr2/words.txt')
				for word in text.split():
					for key in dict:
						if len(word) <= 4:
							if word.lower() == dict[key].lower():
								val[key] = 1
						else:
							if difflib.SequenceMatcher(None, word.lower(), dict[key].lower()).ratio() > 0.70:
								val[key] = 1
				training_data.append(val)
				name = os.path.splitext(os.path.basename(filename))[0]
				#result = ''.join(i for i in name if not i.isdigit())
				result = name[:-2]
				labels.append(result)
				continue
		else:
			continue

	training_data = np.asarray(training_data)
	labels = np.asarray(labels)
	return training_data, labels

dictionary = make_dictionary()
write_to_txt()
my_training_data, my_labels = get_training_data(dictionary)
print(my_training_data)
print(my_labels)
np.save('TrainingData', my_training_data)
np.save('Labels', my_labels)




