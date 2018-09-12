#!/bin/bash -e

version="5.2.0-rb3"
stack="anaconda2-5.1.0"
stack="anaconda2-5.2.0"
#stack="anaconda2-5.2.0-r"

ofile=$(pwd)"/amrdec_stack.tar"
cd /storage/data
#tar -cf ${ofile} *
./${stack}/bin/python -m compileall ${stack}
chmod -R 755 ${stack}
tar -cf ${ofile} ${stack}
#gzip -9f ${ofile}
#ofile+=".gz"

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
md5sum ${insfile} > ${insfile}.md5
7za a -mx=9 ${insfile}.7z ${insfile}
