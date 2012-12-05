function gist = calculateGIST(file_name, train_file)

% GIST Parameters:
clear param
param.imageSize = [32 32];
param.orientationsPerScale = [8 8 8 8]; % number of orientations per scale (from HF to LF)
param.numberBlocks = 4;
param.fc_prefilt = 4;

if (isdir(file_name))
	f = fopen(strcat(file_name, train_file), 'r');
	line = fgetl(f);
	i = 1;
	while ischar(line)
		line = strrep(line, 'tags', 'images');
		line = strrep(line, 'txt', 'jpg');
		fileList{i} = line;
		i = i + 1;
		line = fgetl(f);
	end
	fclose(f);

	i = i - 1;

	file_mapping = cell(length(fileList), 1);
	Nfeatures = sum(param.orientationsPerScale)*param.numberBlocks^2;
	gist = zeros([length(fileList) Nfeatures]); 
	
	% Load first image and compute gist:
	fileName = fileList{1};
	file_mapping{1} = fileName;
	img = imread(fileName);
	[gist(1, :), param] = LMgist(img, '', param); % first call
	
	% Loop:
	for i = 2:length(fileList)
	    fileName = fileList{i};
	    file_mapping{i} = fileName;
	    img = imread(fileName);
		gist(i, :) = LMgist(img, '', param); % the next calls will be faster

		if (mod(i, 100) == 0)
			i
			save('GIST.mat', 'file_mapping', 'gist');
		end
	end

	save('GIST.mat', 'file_mapping', 'gist');
else
    img = imread(file_name);
	
	% Computing gist
	[gist, param] = LMgist(img, '', param);
end

end