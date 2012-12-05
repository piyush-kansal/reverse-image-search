function [ ] = generateHashFile( folderName, hashFileName )

curDir = pwd();
cd(folderName);
fileList = dir('*.jpg');
cd(curDir);

fid = fopen(hashFileName, 'w');

for i=1:length(fileList)
    fileName = fileList(i).name;
    [pHashVec] = pHash(folderName, fileName);
    % disp(pHashVec);
    % pHashVec = [pHashVec];
    fprintf(fid, '%s:%lX\r\n', fileName, pHashVec);
end

fclose(fid);

end