# update the /docs folder from the /build one
# docs is used for the LIVE sample website on Github


DIR_BUILD="build"
DIR_DOCS="docs"

#
# RSync HTML site to docs folder
# https://download.samba.org/pub/rsync/rsync.html
# https://devhints.io/rsync
# opt: -av: recursive and verbose
# opt: --delete: delete files in destination that are not in source
# opt: --checksum: checksum files to see if they have changed (instead of comparing file sizes / modification times)
# opt: --exclude: exclude files from sync
#
echo -e "\nRSYNC TEMP BUILD DIRECTORY INTO FINAL LOCATION:  /$DIR_DOCS"
echo "+++++++++++++++++"
rsync -av --delete --checksum --exclude '.nojekyll' --exclude 'CNAME' $DIR_BUILD/ $DIR_DOCS/

