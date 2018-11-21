%module foo
// #include "foo.h"
// %include "foo.h"
%include "typemaps.i"
%inline %{
extern void ecr2eci(double* a, double* b);
%}
%inline %{
extern void add(double a, double b, double *OUTPUT);
%}
%inline %{
extern void foo(void);
%}
%inline %{
void passFunction(void);
%}
%apply double *OUTPUT { double *opx, double *opy, double *opz, double *ovx, double *ovy, double *ovz};
%inline %{
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
                 double *ovz);
%}
%inline %{
double vincenty(double iLat, double iLon);
%}
%inline %{
void passFunction2(void);
%}
%inline %{
void setGlobals(void);
%}
