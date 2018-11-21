

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
//#include "foo.h"

double c_wgs[6][6] = {{0.0}};

void setGlobals(void)
{
	unsigned char i,j;
	for (i=0;i<6;i++)
	{
		for (j=0;j<6;j++)
		{
			c_wgs[i][j] = i * j * 4.0;
		};
	};
};

struct pVect
{
	double px;
	double py;
	double pz;
	double vx;
	double vy;
	double vz;
	struct pVect *next;
};

//struct pVect *head = NULL;
//struct pVect *curr = NULL;

void editVector(struct pVect *v)
{
	v->px = 1000.0;
};

void propVector(double px,
		double py,
		double pz,
		double vx,
		double vy,
		double vz){
	struct pVect *root;
	struct pVect *ptr;
	root = malloc( sizeof(struct pVect));
	if (root == NULL)
	{
		printf("Node Creation Failed\n");
		return;
	}
	root->px = px;
	root->py = py;
	root->pz = pz;
	root->vx = vx;
	root->vy = vy;
	root->vz = vz;
	ptr = root;
	// Add a new vectors
	for (int i=0;i<15;i++) {
	//printf("Loop %d\n",i);
	ptr->next = malloc(sizeof(struct pVect));
	if ( ptr == NULL )
	{
		printf("Out of Memory\n");
		return;
	}
	// initialize new memory
	ptr = ptr->next;
	ptr->px = px + i;
	ptr->py = py + i * 2;
	ptr->pz = pz + i * 4;
	ptr->vx = vx + i * 6;
	ptr->vy = vy + i * 7;
	ptr->vz = vz + i * 10;
	}
	editVector(ptr);
	// print out contents
	ptr = root;
	//editVector(ptr);
	while ( ptr != NULL ){
	//for (int i=0;i<16;i++){
		printf("%.2f,%.2f,%.2f,",ptr->px,ptr->py,ptr->pz);
		printf("%.2f,%.2f,%.2f\n",ptr->vx,ptr->vy,ptr->vz);
		printf("***\n");
		ptr = ptr->next;
	};
	
};

void propVector2(double px,
		double py,
		double pz,
		double vx,
		double vy,
		double vz,
		double *opx,
		double *opy,
		double *opz,
		double *ovx,
		double *ovy,
		double *ovz){
	*opx = px + 1.0;
	*opy = py + 2.0;
	*opz = pz + 3.0;
	*ovx = vx + 4.0;
	*ovy = vy + 5.0;
	*ovz = vz + 6.0;
};

void add(double x, double y, double *result){
	*result = x + y;
};

void callPropVector(double *s)
{

	propVector(s[0],s[1],s[2],s[3],s[4],s[5]);
};


void foo(void)
{
	puts("Hello, I'm a shared libray");
	printf("Goodbye\n");
}

double get3(int x)
{
	double tmp = x;
	return 3.0 * tmp;
}

void ecr2eci(double *eci, double *ecr)
{
	eci[0] = ecr[0];
	eci[1] = 1.;
	eci[2] = 60.;
}

void propVectorORIG(double* ivect)
{
	// assume it is a 4-state vector
	//size_t nv = 4 * sizeof(double);

	unsigned char i = 3,j,k;
	for (j = 0; j < 3; j++)
	{
		ivect = realloc(ivect,4);
		printf("here\n");
		ivect[i+1] = 140.0;
		printf("i+1\n");
		ivect[i+2] = 566373.9;
		ivect[i+3] = 88773.88;
		ivect[i+4] = 0.0;
		printf("i+4\n");
		for (k=0; k < 12; k++) printf("%f\n",ivect[k]);
		i += 4;
	}
};

void printPoly(double (*ip)[18])
{
	unsigned char i,j;
	for (i=0;i<18;i++)
	{
		for (j=0;j<18;j++)
		{
			printf("%3.1f ",ip[i][j]);
		}
		printf("\n");
	}
};

void editPoly(double *po, double (*p)[18])
{
	unsigned char i,j;
	double di = 0.0;
	for (i=0;i<18;i++)
	{
		po[i] = 0.0;
		for (j=0;j<18;j++)
		{
			di += 1.0;
			p[i][j] = di;
		}
	}
};
void print1dArray(int nr, double *p)
{
	for (int i=0;i<nr;i++)
	{
		printf("%3.1f ",p[i]);
	};
printf("\n");
};

void print2dArray(int nr, int nc,double p[][nc])
{
	int i,j;
	for (i=0;i<nr;i++)
	{
		for (j=0;j<nc;j++)
		{
			printf("%3.1f ",p[i][j]);
		};
		printf("\n");
	};
};
void passFunction(void)
{
	/*double po[18] = {0.0};
	double p[18][18] = {{0.0}};
	printPoly(p);
	editPoly(po,p,4.0);
	printf("***\n");
	print2dArray(18,18,p);
	printf("***\n");
	for (int i=0;i<18;i++) {for (int j=0;j<18;j++) {p[i][j] = 0.0;}}
	print2dArray(18,18,p);*/
	print2dArray(6,6,c_wgs);
	setGlobals();
	print2dArray(6,6,c_wgs);
};

void passFunction2(void)
{
	print2dArray(6,6,c_wgs);
};

double vincenty(double iLat, double iLon)
{
	double tmp;
	unsigned short i = 0;
	while (i < 1000)
	{
		i += 1;
		tmp = pow(sin(iLat),iLon);
	};
	return tmp;
};


