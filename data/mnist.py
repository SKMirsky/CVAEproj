###
'''
Borrowed from original implementation: https://github.com/dpkingma/nips14-ssl (anglepy)
'''
###

import numpy as np
import _pickle, gzip
import data
import os

def load_numpy(path, binarize_y=False):
    # MNIST dataset
    if os.getcwd() not in path: path = os.getcwd() + '/' + path
    f = gzip.open(path, 'rb')
    train, valid, test = _pickle.load(f, encoding='iso-8859-1') # Work around to fix incompatibility issues between python 2.x and 3.x
    f.close()
    train_x, train_y = train
    valid_x, valid_y = valid
    test_x, test_y = test
    if binarize_y:
        train_y = binarize_labels(train_y)
        valid_y = binarize_labels(valid_y)
        test_y = binarize_labels(test_y)
        
    return train_x.T, train_y, valid_x.T, valid_y, test_x.T, test_y

# Loads data where data is split into class labels
def load_numpy_split(path, binarize_y=False, n_train=50000):
    path = os.getcwd() + '/' + path
    train_x, train_y, valid_x, valid_y, test_x, test_y = load_numpy(path,False)

    train_x = train_x[0:n_train]
    train_y = train_y[0:n_train]
    
    def split_by_class(x, y, num_classes):
        result_x = [0]*num_classes
        result_y = [0]*num_classes
        for i in range(num_classes):
            idx_i = np.where(y == i)[0]
            result_x[i] = x[:,idx_i]
            result_y[i] = y[idx_i]
        return result_x, result_y
    
    train_x, train_y = split_by_class(train_x, train_y, 10)
    if binarize_y:
        valid_y = binarize_labels(valid_y)
        test_y = binarize_labels(test_y)
        for i in range(10):
            train_y[i] = binarize_labels(train_y[i])
    return train_x, train_y, valid_x, valid_y, test_x, test_y


# Converts integer labels to binarized labels (1-of-K coding)
def binarize_labels(y, n_classes=10):
    new_y = np.zeros((n_classes, y.shape[0]))
    for i in range(y.shape[0]):
        new_y[y[i], i] = 1
    return new_y

def unbinarize_labels(y):
    return np.argmax(y,axis=0)
    
def save_reshaped(shape):
    def reshape_digits(x, shape):
        def rebin(a, shape):
            sh = shape[0],a.shape[0]//shape[0],shape[1],a.shape[1]//shape[1]
            return a.reshape(sh).mean(-1).mean(1)
        nrows = x.shape[0]
        ncols = shape[0]*shape[1]
        result = np.zeros((nrows, ncols))
        for i in range(nrows):
            result[i,:] = rebin(x[i,:].reshape((28,28)), shape).reshape((1, ncols))
        return result

    # MNIST dataset
    f = gzip.open(paths[28], 'rb')
    train, valid, test = _pickle.load(f)
    train = reshape_digits(train[0], shape), train[1]
    valid = reshape_digits(valid[0], shape), valid[1]
    test = reshape_digits(test[0], shape), test[1]
    f.close()
    f = gzip.open(os.path.dirname(__file__)+'/mnist_'+str(shape[0])+'_.pkl.gz','wb')
    _pickle.dump((train, valid, test), f)
    f.close()
    
def make_random_projection(shape):
    W = np.random.uniform(low=-1, high=1, size=shape)
    W /= (np.sum(W**2,axis=1)**(1./2)).reshape((shape[0],1))
    return W


# Create semi-supervised sets of labeled and unlabeled data
# where there are equal number of labels from each class
# 'x': MNIST images
# 'y': MNIST labels (binarized / 1-of-K coded)
def create_semisupervised(x, y, n_labeled):
    import random
    n_x = x[0].shape[0]
    n_classes = y[0].shape[0]
    if n_labeled%n_classes != 0: raise("n_labeled (wished number of labeled samples) not divisible by n_classes (number of classes)")
    n_labels_per_class = n_labeled/n_classes
    x_labeled = [0]*n_classes
    x_unlabeled = [0]*n_classes
    y_labeled = [0]*n_classes
    y_unlabeled = [0]*n_classes
    for i in range(n_classes):
        idx = range(x[i].shape[1])
        random.shuffle(idx)
        x_labeled[i] = x[i][:,idx[:n_labels_per_class]]
        y_labeled[i] = y[i][:,idx[:n_labels_per_class]]
        x_unlabeled[i] = x[i][:,idx[n_labels_per_class:]]
        y_unlabeled[i] = y[i][:,idx[n_labels_per_class:]]
    return np.hstack(x_labeled), np.hstack(y_labeled), np.hstack(x_unlabeled), np.hstack(y_unlabeled)
        
        