#!/bin/bash

version="5.2.0-rb2"
stack="anaconda2-5.1.0"
stack="anaconda2-5.2.0"
stack="anaconda2-5.2.0-r"

ofile=$(pwd)"/amrdec_stack.tar"
cd /storage/data
#tar -cf ${ofile} *
tar -cf ${ofile} ${stack}
#gzip -9f ${ofile}
#ofile+=".gz"

insfile="installAmrdec-${version}.sh"
cd -
echo '#!/bin/bash' > ${insfile}
echo '' >> ${insfile}
cat install.sh.in >> ${insfile}
echo "SOFTWARE:" >> ${insfile}
cat ${ofile} >> ${insfile}
chmod 755 ${insfile}
rm ${ofile}
md5sum ${insfile} > ${insfile}.md5
7za a -mx=9 ${insfile}.7z ${insfile}
