from src import Classifier as cl

if __name__ == '__main__':
    # Test data
    x = [[1, 0, 0, 0 , 0, 0, 0, 0, 0, 0, 1],
         [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0]]
    y = [3, 4]

    spcl = cl.MLClassifier(feature_extraction=None)
    spcl.fit(x, y)

    print(spcl.predict([[1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1], [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0]]))
