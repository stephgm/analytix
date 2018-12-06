
#ifndef foo_h_
#define foo_h_

extern void foo(void);
/*struct pVect
{
	double px;
	double py;
	double pz;
	double vx;
	double vy;
	double vz;
	struct pVect *next;
};*/
extern void propVector(double,double,double,double,double,double);
extern void propVector2(double,double,double,double,double,double,double*,double*,double*,double*,double*,double*);
extern void callPropVector(double *);
extern void passFunction(void);
extern void passFunction2(void);
extern double vincenty(double,double);
void setGlobals(void);
//extern double get3(int);
extern void ecr2eci(double*,double*);
extern void editPoly(double *po, double (*p)[18]);
extern void print2dArray(int nr, int nc,double p[][nc]);
extern void printPoly(double (*ip)[18]);
extern void print1dArray(int nr, double *p);
//extern void propVector(double*);

#endif // foo_h_
