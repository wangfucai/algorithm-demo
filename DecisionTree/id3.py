#coding=utf-8
import math
import operator

#计算给定数据shangnon数据的函数：
def calcShannonEnt(dataSet):
    #calculate the shannon value
    numEntries = len(dataSet)
    labelCounts = {}
    for featVec in dataSet:      #create the dictionary for all of the data
        currentLabel = featVec[-1]
        if currentLabel not in labelCounts.keys():
            labelCounts[currentLabel] = 0
        labelCounts[currentLabel] += 1
    shannonEnt = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key])/numEntries
        shannonEnt -= prob*math.log(prob,2) #get the log value
    return shannonEnt

#创建数据的函数
"""
def createDataSet():
    dataSet = [[1,1,'yes'],
               [1,1, 'yes'],
               [1,0,'no'],
               [0,1,'no'],
               [0,1,'no']]
    labels = ['no surfacing','flippers']
    return dataSet, labels
"""
#天气-晴朗（0），多云（1），下雨（2）
#温度-热（0），适中（1），冷（2）
#湿度-高（0），正常（1）
#风-无风（0），有风（1）
#是否可以玩-可以（yes），不可以（no）
def createDataSet():
    dataSet = [[0, 0, 0, 0, 'no'],
               [0, 0, 0, 1, 'no'],
               [1, 0, 0, 0, 'yes'],
               [2, 1, 0, 0, 'yes'],
               [2, 2, 1, 0, 'yes'],
               [2, 2, 1, 1, 'no'],
               [1, 2, 1, 1, 'yes'],
               [0, 1, 0, 0, 'no'],
               [0, 2, 1, 0, 'yes'],
               [2, 1, 1, 0, 'yes'],
               [0, 1, 1, 0, 'yes'],
               [1, 1, 0, 1, 'yes'],
               [1, 0, 1, 0, 'yes'],
               [2, 1, 0, 1, 'no']]
    #labels = ['天气','温度','湿度','风']
    labels = ['outlook', 'temperature', 'humidity', 'windy']
    return dataSet, labels

#划分数据集，按照给定的特征划分数据集
def splitDataSet(dataSet, axis, value):
    retDataSet = []
    for featVec in dataSet:
        if featVec[axis] == value:      #abstract the fature
            reducedFeatVec = featVec[:axis]
            reducedFeatVec.extend(featVec[axis+1:])
            retDataSet.append(reducedFeatVec)
    return retDataSet

#选择最好的数据集划分方式
def chooseBestFeatureToSplit(dataSet):
    numFeatures = len(dataSet[0])-1
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGain = 0.0; bestFeature = -1
    for i in range(numFeatures):
        featList = [example[i] for example in dataSet]
        uniqueVals = set(featList)
        newEntropy = 0.0
        for value in uniqueVals:
            subDataSet = splitDataSet(dataSet, i , value)
            prob = len(subDataSet)/float(len(dataSet))
            newEntropy +=prob * calcShannonEnt(subDataSet)
        infoGain = baseEntropy - newEntropy
        if(infoGain > bestInfoGain):
            bestInfoGain = infoGain
            bestFeature = i
    return bestFeature

#递归创建树,用于找出出现次数最多的分类名称的函数
def majorityCnt(classList):
    classCount = {}
    for vote in classList:
        if vote not in classCount.keys(): classCount[vote] = 0
        classCount[vote] += 1
    sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]

#递归创建树,用于创建树的函数代码
def createTree(dataSet, labels):
    classList = [example[-1] for example in dataSet]
    # the type is the same, so stop classify
    if classList.count(classList[0]) == len(classList):
        return classList[0]
    # traversal all the features and choose the most frequent feature
    if (len(dataSet[0]) == 1):
        return majorityCnt(classList)
    bestFeat = chooseBestFeatureToSplit(dataSet)
    print('bestFeat =' + str(bestFeat))
    bestFeatLabel = labels[bestFeat]
    myTree = {bestFeatLabel:{}}
    del(labels[bestFeat])
    #get the list which attain the whole properties
    featValues = [example[bestFeat] for example in dataSet]
    print(bestFeatLabel)
    print(featValues)
    uniqueVals = set(featValues)
    print(uniqueVals)
    for value in uniqueVals:
        subLabels = labels[:]
        myTree[bestFeatLabel][value] = createTree(splitDataSet(dataSet, bestFeat, value), subLabels)
    return myTree

#实用决策树进行分类的函数
def classify(inputTree, featLabels, testVec):
    #firstStr = inputTree.keys()[0]
    firstStr = list(inputTree.keys())[0]
    secondDict = inputTree[firstStr]
    featIndex = featLabels.index(firstStr)
    for key in secondDict.keys():
        if testVec[featIndex] == key:
            if type(secondDict[key]).__name__ == 'dict':
                classLabel = classify(secondDict[key], featLabels, testVec)
            else: classLabel = secondDict[key]
    return classLabel

myDat, labels = createDataSet()
myTree = createTree(myDat,labels)
myDat, labels = createDataSet()
print(myTree)
print(classify(myTree,labels,[0,0,1,1]))