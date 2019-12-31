'''
models.py

part of the wordfish python package: specific machine learning models

Copyright (c) 2015-2018 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to 
do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included 
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

from random import sample
from sklearn import svm
import pandas
import math
import sys
import os

def build_svm(vectors,labels,kernel="linear",positive_label=1,negative_label=0,testing_holdout=0.2):
    '''build_svm
    vectors: a data frame of vectors to be used for training and testing
    labels: a pandas data frame of objects (rows) and labels (columns)
    labels.index should correspond with vectors.index
    '''
    classifiers = pandas.DataFrame(columns=["accuracy","N","term","N_train","N_test","testNPos",
                               "testNNeg","trainNPos","trainNNeg","TP","FP","TN","FN","kernel"])
    term_names = labels.columns.tolist()
    for term in term_names:
        if "%s_%s" %(term,kernel) not in classifiers.index:
            data_Y = labels[term]
            positive_examples = data_Y.index[data_Y==positive_label]
            negative_examples = data_Y.index[data_Y==negative_label]
            # hold out some percentage of each for testing
            testSizePositive = int(math.ceil(len(positive_examples)*testing_holdout))
            testSizeNegative = int(math.ceil(len(negative_examples)*testing_holdout))
            testN = testSizePositive + testSizeNegative
            testPos = sample(positive_examples, testSizePositive)
            testNeg = sample(negative_examples, testSizeNegative)
            test = vectors.loc[testPos+testNeg]
            test_Y = [term if x in testPos else "not %s" %(term) for x in test.index]
            trainPos = [x for x in positive_examples if x not in testPos]
            trainNeg = [x for x in negative_examples if x not in testNeg]
            trainN = len(trainPos) + len(trainNeg)
            train = vectors.loc[trainPos+trainNeg]
            train_Y = [term if x in trainPos else "not %s" %(term) for x in train.index]
            clf = svm.SVC(kernel=kernel)
            clf.fit(train, train_Y)
            # Make a single prediction based on vectors
            predictions=[]
            for t in test.index:
                predictions.append(clf.predict(test.loc[t])[0])
            correct = float(len([x for x in range(len(predictions)) if predictions[x]==test_Y[x]]))
            accuracy = correct / len(test_Y)
            positive_predictions = [x for x in range(len(predictions)) if predictions[x] == term]
            negative_predictions = [x for x in range(len(predictions)) if predictions[x] == "not %s" %term]
            positive_actual = [x for x in range(len(test_Y)) if test_Y[x] == term]
            negative_actual = [x for x in range(len(test_Y)) if test_Y[x] == "not %s" %term]
            TP = len([x for x in positive_actual if x in positive_predictions])
            TN = len([x for x in negative_actual if x in negative_predictions])
            FP = len([x for x in negative_actual if x in positive_predictions])
            FN = len([x for x in positive_actual if x in negative_predictions])
            classifiers.loc["%s_%s" %(term,kernel)] = [accuracy,len(data_Y),term,trainN,testN,len(testPos),len(testNeg),len(trainPos),len(trainNeg),TP,FP,TN,FN,kernel]

    return classifiers
