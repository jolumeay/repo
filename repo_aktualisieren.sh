#!/bin/bash
# Author: L0RE
# This Script Generates a new Inventory for a new Version or New Plugin
REPO=/www/repo/gitnew
cd $REPO/addons
echo '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' >$REPO/addons.xml
echo '<addons>' >> $REPO/addons.xml
for name in *; do 
   VERSION=`cat $name/addon.xml|grep \<addon|grep $name |sed 's/.*version="\([^"]*\)"*.*/\1/g'`
     if [ ! -f "$name/$name-$VERSION.zip" ]; then
       zip -r $name/$name-$VERSION.zip $name -x \*.zip
     fi
   cat $name/addon.xml|grep -v "<?xml " >> $REPO/addons.xml
   echo "" >> $REPO/addons.xml
 done
 echo "</addons>" >> $REPO/addons.xml
 md5sum  /www/repo/gitnew/addons.xml > $REPO/addons.xml.md5
