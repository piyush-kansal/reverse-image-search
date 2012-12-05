% inputs:
% 	queryTagFile -- the tag filename of an input query image
% outputs:
%	closestmatches -- a cell array with the filenames of the 10 most similar images to the query

function [] = imageRetrieval_text(queryTagFile, outputFile)

% Make a hash table of all the vocab words
fid = fopen('vocab.dat');
vocabwords = textscan(fid, '%s');
fclose(fid);
vocabwords = vocabwords{1,:};

vocabwords_map = containers.Map('KeyType', 'char', 'ValueType', 'uint64');
for i=1:length(vocabwords)
	vocabwords_map(vocabwords{i,:}) = i;
end

% Compute query vector descriptor for the query tag file
queryVector = zeros(1, length(vocabwords), 'int8');
fid = fopen(queryTagFile, 'r');
words = textscan(fid, '%s');
fclose(fid);
words = words{1,:};

for k = 1:length(words)
	curword = words{k,:};
	queryVector(1, vocabwords_map(curword)) = queryVector(1, vocabwords_map(curword)) + 1;
end

% Compute word vector descriptor for the word tag files
% - create 1000 buckets of 400 files each
% - sort each buck
% - using external sort, find 400 minimum SSD values
fid = fopen('fileList.dat', 'r');
fileList = textscan(fid, '%s');
fclose(fid);
fileList = fileList{1,:};

bucketVector = zeros(400, length(vocabwords), 'int8');
sortedFileList = {};
for startIndex=1:1000
	% For all the text files, do following:
	% - read text file
	% - read all the words in an array
	% - for each word in this array, increment the value in the
	%   corresponding row and column
	bucketVector(:,:) = 0;

	startIndex
	for i=1:400
		index = (startIndex-1)*400 + i;
		fid = fopen(fileList{index}, 'r');
		words = textscan(fid, '%s');
		fclose(fid);
		words = words{1,:};

		for k = 1:length(words)
			curword = words{k,:};
			bucketVector(i, vocabwords_map(curword)) = bucketVector(i, vocabwords_map(curword)) + 1;
		end

		% compute SSD between the query descriptor and each database image descriptor here
		temp_ssd{i} = {fileList{index}, sum(sum((queryVector(1,:) - bucketVector(i,:)).^2))};
	end

	if startIndex == 1
		sortedFileList = temp_ssd;
	else
		for j=1:400
			sortedFileList{end+1} = temp_ssd{j};
		end
	end
end

[vals, order] = sort(cellfun(@(x) x{2}, sortedFileList));
sortedFileList = sortedFileList(order);

fid = fopen(outputFile, 'w');
for i=1:1000
	fprintf(fid, '%s\n', sortedFileList{i}{1});
end
fclose(fid);