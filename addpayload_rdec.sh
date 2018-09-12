#!/bin/bash -e

version="5.2.0-rb4"
stack="anaconda2-5.1.0"
stack="anaconda2-5.2.0"
#stack="anaconda2-5.2.0-r"
echo -n "tar..."
ofile=$(pwd)"/amrdec_stack.tar"
cd /storage/data
echo -n "compile.."
./${stack}/bin/python -m compileall ${stack} > /dev/null 2>&1 || echo -n "."
echo -n "chmod..."
chmod -R 755 ${stack}
tar -cf ${ofile} ${stack}
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
7za a -mx=9 ${insfile}.7z ${insfile}
echo "done"
