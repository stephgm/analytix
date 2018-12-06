
#include <stdio.h>
#include <math.h>
#include "foo.h"

//void ecr2eci(double* , double*);
//extern void foo(void);
// void printPoly(double (*ip)[18]);
// void editPoly(double *po, double (*p)[18]);
// void print2dArray(int nr, int nc,double p[][nc]);

int main(void)
{
//puts("This is shared library test ... ");
//foo();
//propVector(1.0,2.0,3.0,4.0,5.0,6.6);
//double a[6] = {1.0,2.0,3.0,4.0,5.0,6.6};
//callPropVector(a);
//passFunction();
/*
printf("initializing ... \n");
passFunction2();
printf("Setting globals ... ");
setGlobals();
printf("calling again ... \n");
passFunction2();
printf("done\n");
*/
//double tmp = vincenty(14.0, 15.0);
//printf("Vincenty: %20.20f\n",tmp);
/*int i;
double a[4] = {13.4432,48873465.29,0.0,0.0};
FILE *ptr;
ptr = fopen("data.bin","w");
for (i=0;i<4;i++)
{
	fwrite(&a[i],sizeof(double),1,ptr);
};
fclose(ptr);
*/
double p[18],po[18][18];
// print1dArray(18,p);
// print2dArray(18,18,po);
editPoly(p,po);
// printf("\n***\n");
print1dArray(18,p);
print2dArray(18,18,po);
return 0;
}
