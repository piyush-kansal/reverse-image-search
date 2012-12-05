function queryImage(img_file_name, train_file, output_file)
	clear SHparam score;
	colors = 'cbmrg';

	% Calculate GIST for training images
	Xtraining = calculateGIST('./', train_file);

	% Train classifier using 32 bit	
	SHparam.nbits = 32;
	SHparam = trainSH(Xtraining, SHparam);
	save('GIST.mat', 'SHparam', '-append');

	% Compress training set
	[B1,U1] = compressSH(Xtraining, SHparam);
	save('GIST.mat', 'B1', 'U1', '-append');

	% Calculate GIST and compress on query image
	Xtest = calculateGIST(img_file_name);
	[B2,U2] = compressSH(Xtest, SHparam);
	save('GIST.mat', 'B2', 'U2', '-append');

	% Calculate hamming distance on training and test images
	Dhamm = hammingDist(B2, B1);
	save('GIST.mat', 'Dhamm', '-append');

	% Find index of similar images
	j = 1;
	for i=1:length(Dhamm)
		if ( Dhamm(i) < 7 )
			res(j) = i;
			j = j + 1;
		end
	end

	j = j - 1

	% Show similar images to user
	load('GIST.mat', 'file_mapping');
	fid = fopen(output_file, 'w');

	for i=1:j
		fprintf(fid, '%s\n', file_mapping{res(i)});
		imshow(file_mapping{res(i)});
		pause(1)
	end
	
	fclose(fid);

	end