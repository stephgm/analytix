#ANACONDA_INC=/storage/data/local/include/python2.7
#ANACONDA_INC=/storage/data/local/include/python3.6m
ANACONDA_INC=/storage/data/local/include/python3.7m

test: main.c libfoo.so _foo.so
	#gcc --version
	gcc -O3 -g -L. -o test main.c -lfoo
_foo.so: interface_wrap.o foo.o
	gcc -O3 -shared interface_wrap.o foo.o -o _foo.so
interface_wrap.o: interface_wrap.c
	#gcc -O3 -c -fPIC interface_wrap.c -I/usr/include/python2.7
	#gcc -O3 -c -fPIC interface_wrap.c -I${ANACONDA_LOCAL}/include/python2.7
	gcc -O3 -c -fPIC interface_wrap.c -I$(ANACONDA_INC)
libfoo.so: foo.o
	gcc -O3 -g -shared -o libfoo.so foo.o -lm
foo.o: foo.c foo.h
	gcc -O3 -c -Wall -Werror -fPIC foo.c
clean:
	if [ -e foo.o ];then rm foo.o;fi
	if [ -e libfoo.so ];then rm libfoo.so;fi
	if [ -f test ];then rm test;fi
	if [ -e _foo.so ];then rm _foo.so;fi
	if [ -e interface_wrap.o ];then rm interface_wrap.o;fi
