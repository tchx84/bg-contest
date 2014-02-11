filename='contest.db';
backupdir='backups';
filetime=$(date +%Y%m%d_%H%M%S);
cp ${filename} ${backupdir}/${filename}_${filetime};
