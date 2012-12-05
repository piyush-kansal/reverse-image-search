function [ pHashVec ] = pHash( folderName, imgFilename )

curDir = pwd();
cd(folderName);

img = im2double(imread(imgFilename));
img = imresize(img, [32, 32]);
grayImg = rgb2gray(img);

dctImg = dct2(grayImg);
dct1 = 0;
for i=1:8
    for j=1:8
        dct1 = dct1 + dctImg(i,j);
    end
end

dct1 = dct1 - dctImg(1,1);
avgVal = dct1/63;

pHashVec = 0;
pHashVec = uint64(pHashVec);
for i = 1:8
    for j = 1:8
        if(i == 0 && j == 0) continue; end
        if(dctImg(i,j) > avgVal)
            pHashVec = bitset(pHashVec, (i-1)*8 + j);
        end
    end
end

cd(curDir);

end