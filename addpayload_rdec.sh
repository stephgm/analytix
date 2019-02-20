#!/bin/bash -e

version="5b1"
version="py3-5b0"

stack=$(basename $(readlink /storage/data/local))
while (( $# ));do
if [ "$1" == "-v" ];then
    shift
    version="$1"
fi
shift
done
echo $version

#stack="anaconda2-5.2.0-r"
echo -n "tar..."
ofile=$(pwd)"/amrdec_stack.tar"
cd /storage/data
echo -n "compile.."
./${stack}/bin/python -m compileall ${stack} > /dev/null 2>&1 || echo -n "."
echo -n "chmod..."
chmod -R 755 ${stack}
echo -n "tar..."
tar -cf ${ofile} ${stack}
#touch ${ofile}
echo -n "payloding..."
insfile="installAmrdec-${version}.sh"
cd -
echo '#!/bin/bash' > ${insfile}
echo '' >> ${insfile}
echo 'idir='${stack} >> ${insfile}
cat install.sh.in >> ${insfile}
echo "SOFTWARE:" >> ${insfile}
cat ${ofile} >> ${insfile}
chmod 755 ${insfile}
rm ${ofile}
echo -n "md5sum..."
md5sum ${insfile} > ${insfile}.md5
echo -n "compressing..."
#7za a -mx=9 ${insfile}.7z ${insfile}
xz -9 -e ${insfile}
echo "done"
