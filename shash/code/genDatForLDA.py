# Main script for generating .dat file as an i/p to LDA program
# Piyush Kansal and Vinak K

import sys
import os
import pickle
import subprocess as sp
import operator
import threading
import time

global vocabFileName, wordLexiconFileName, wordCount

# Function to process all the tags in the data set to generate
# i/p for LDA program
def genInputForLDA(dataSetFolder):
	tagsFolder = dataSetFolder + '\\' + 'tags' + '\\'
	vocabFileName = 'vocab.dat'
	wordLexiconFileName = 'wordLexicon.dat'
	wordFileMapping = 'wordFileMapping.dat'
	fileOrder = 'fileOrder.dat'
	wordCountFileName = 'wordCount.dat'
	global memo2, fileMemo

	if not os.path.isfile(vocabFileName):
		vocab = []
		files = []
		
		for dirname in os.listdir(tagsFolder):
			folder = os.path.join(tagsFolder, dirname)

			for subdirname in os.listdir(folder):
				subfolder = os.path.join(folder, subdirname)

				for curfile in os.listdir(subfolder):
					fileName = os.path.join(subfolder, curfile)
					files.append(fileName)
					with open(fileName, 'r') as f:
						vocab += f.readlines()

		vocab = list(set(vocab))
		with open(vocabFileName, 'w') as vocabFile:
			vocabFile.write(''.join(vocab))

		fileMemo = {}
		for index, curfile in enumerate(files):
			fileMemo[curfile] = index

		with open(fileOrder, 'wb') as f:
			pickle.dump(fileMemo, f)

		vocabDict = {}
		for index, item in enumerate(vocab):
			vocabDict[item] = index

		datFile = open(wordLexiconFileName, 'w')
		wordCountFile = open(wordCountFileName, 'wb')
		memo2 = {}
		wordCount = {}
		for curfile in files:
			lines = None
			with open(curfile, 'r') as f:
				lines = f.readlines()

			memo = {}
			for item in lines:
				if item in memo:
					memo[item] += 1
				else:
					memo[item] = 1

				if item in memo2:
					if curfile not in memo2[item]:
						memo2[item].append(curfile)
				else:
					memo2[item] = []
					memo2[item].append(curfile)

			opLine = str(len(memo))
			for k, v in memo.items():
				opLine += ' ' + str(vocabDict[k]) + ':' + str(v)
			
			datFile.write(opLine)
			datFile.write('\n')
			wordCount[curfile] = memo
		
		datFile.close()
		pickle.dump(wordCount, wordCountFile)
		wordCountFile.close()

		with open(wordFileMapping, 'wb') as wordFile:
			pickle.dump(memo2, wordFile)

	else:
		with open(wordFileMapping, 'rb') as f:
			memo2 = pickle.load(f)

		with open(fileOrder, 'rb') as f:
			fileMemo = pickle.load(f)


def genSynsetsLDA(alpha, numTopics):
	topicsFile = 'p%d\\topics.dat' % (numTopics)
	if not os.path.isfile(topicsFile):
		fileName = 'p%d\\final.beta' % (numTopics)
		if not os.path.isfile(fileName):
			cmd = 'lda est %f %d settings.txt %s random p%d' % (alpha, numTopics, wordLexiconFileName, numTopics)
			r = sp.call(cmd.split())
			if r:
				print 'Some error occured during LDA Estimation. Exiting ...'
				sys.exit(r)

		gammaFile = 'p%d\\inf-gamma.dat' % (numTopics)
		if not os.path.isfile(gammaFile):
			cmd = 'lda inf settings.txt p%d\\final %s p%d\\inf' % (numTopics, wordLexiconFileName, numTopics)
			r = sp.call(cmd.split())
			if r:
				print 'Some error occured during topic inference. Exiting ...'
				sys.exit(r)

		cmd = 'C:\Python27\python.exe topics.py p%d\\final.beta %s %d' % (numTopics, vocabFileName, numTopics)
		with open(topicsFile, 'w') as f:
			r = sp.call(cmd.split(), stdout=f)
			if r:
				print 'Some error occured during topic finding. Exiting ...'
				sys.exit(r)


def findTopic(itemIndex, topicIndex, numTopics):
	curTopicIndex = float("+inf")
	nextTopicIndex = None

	idx = itemIndex/(numTopics + 1)
	curTopicIndex = topicIndex[idx]
	if (idx + 1) <= len(topicIndex):
		nextTopicIndex = topicIndex[idx + 1]

	return curTopicIndex, nextTopicIndex


def calSSD(wordCount, mainMemo, lines, ssd, start, count):
	index = 0
	for line in lines[start:count]:
		line = line.strip('\n')

		memo = mainMemo
		for k, v in wordCount[line].items():
			if k in memo:
				if memo[k][0] == 1:
					memo[k] = (1, memo[k][1] - v)
				else:
					memo[k] = (2, memo[k][1] + v)
			else:
				memo[k] = (2,v)

		total = 0
		for k, v in memo.items():
			total += v[1]**2
		
		ssd[index + start] = (index + start, total)
		print start, index

		index += 1


def findClosestMatchingFiles(queryTagFile, outputFile):
	cmd = 'matlab -r imageRetrieval_text(\'%s\', \'%s\') -nosplash -nodesktop' % (queryTagFile, outputFile)
	sp.call(cmd.split())

	while not os.path.isfile(outputFile):
		time.sleep(600)

	with open(outputFile, 'r') as f:
		if len(f.readlines()) < 1000:
			time.sleep(60)


def getTwoHighestWeightedTopics(queryTagFile, numTopics):
	gammaFile = 'p%d\\inf-gamma.dat' % (numTopics)
	f = open(gammaFile, 'r')
	for index, line in enumerate(f):
		if index == fileMemo[queryTagFile]:
			queryTopicWeights = [(index, float(item)) for index, item in enumerate(line.split())]
			queryTopicWeights.sort(key=operator.itemgetter(1), reverse=True)
			return queryTopicWeights[0], queryTopicWeights[1]


def getWordsInTopic(topicIndex, numTopics):
	topicsFile = 'p%d\\topics.dat' % (numTopics)
	
	with open(topicsFile, 'r') as f:
		topicLines = f.readlines()
		topicLines = map(lambda s: s.strip(' '), topicLines)
		topicLines = filter(lambda s: s != '\n', topicLines)
		topicLines = map(lambda s: s.strip('\n'), topicLines)

	searchWord = 'topic %03d' % (topicIndex)
	index = topicLines.index(searchWord)
	index += 1
	return topicLines[index:index+10]


def getFilesRelatedToTopic(topic, numTopics):
	words = getWordsInTopic(topic[0], numTopics)
	fileCount = {}
	for word in words:
		files = memo2[word]

		for curfile in files:
			if curfile in fileCount:
				fileCount[curfile] += 1
			else:
				fileCount[curfile] = 1

	resultantFiles = []
	for k, v in fileCount.items():
		resultantFiles.append((k, v*topic[1]))

	return resultantFiles


def getFilesRelatedToAllTopicsWeighted(firstTopic, secondTopic, numTopics):
	resultantFiles = getFilesRelatedToTopic(firstTopic, numTopics)
	resultantFiles += getFilesRelatedToTopic(secondTopic, numTopics)

	# Now sort and pick files having count = 10, 9 ... 1
	# till you reach 2000 files
	resultantFiles.sort(key=operator.itemgetter(1), reverse=True)
	return list(set([item[0] for item in resultantFiles]))


def findSimilarFiles(queryTagFile, numTopics, outputFile):
	firstTopic, secondTopic = getTwoHighestWeightedTopics(queryTagFile, numTopics)
	files = getFilesRelatedToAllTopicsWeighted(firstTopic, secondTopic, numTopics)

	newoutputFile = outputFile.split('.')[0] + '_' + str(numTopics) + '.dat'
	with open(outputFile, 'r') as f:
		prevFiles = f.readlines()
		prevFiles = map(lambda s: s.strip('\n'), prevFiles)

	prevFiles += files

	with open(newoutputFile, 'w') as f:
		f.write('\n'.join(prevFiles[:3000]))


def findMatchingWords(queryImage, numTopics, outputFile):
	if os.path.isfile(queryImage):
		queryTagFile = queryImage.split('.jpg')[0] + '.txt'
		queryTagFile = queryTagFile.replace('images', 'tags')

		# Step 1 - find closest matching files using SSD
		if not os.path.isfile(outputFile):
			findClosestMatchingFiles(queryTagFile, outputFile)

		findSimilarFiles(queryTagFile, numTopics, outputFile)

	else:
		print 'Image not found'
		sys.exit(1)


if __name__ == "__main__":
	# take data set folder as i/p from user
	dataSetFolder = sys.argv[1]
	queryImage = sys.argv[2]
	numTopics = int(sys.argv[3])
	imageId = ((queryImage.split('\\'))[-1]).split('.')[0]
	outputFile = 'trainFiles_%s.dat' % (imageId)
	newoutputFile = outputFile.split('.')[0] + '_' + str(numTopics) + '.dat'

	if not os.path.isfile(newoutputFile):
		# generate i/p for LDA program
		genInputForLDA(dataSetFolder)

		# # process using LDA to generate topics and similar words
		genSynsetsLDA(0.5, numTopics)

		# Find matching words between query image and topics generated by LDA
		# and generate a list of files to train
		findMatchingWords(queryImage, numTopics, outputFile)
