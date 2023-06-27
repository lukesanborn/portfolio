#pragma once

#include <cmath>
#include "Common.h"


class Vect
{
public:
    double elem[3];

public:
    void Set(double,
             double,
             double);

    void Print();

    Vect operator+(const Vect other) const;
    Vect operator*(const double d) const;
    Vect operator-() const;
    double &operator[](const int index);
    void operator=(const Vect &other);
};

class DCM
{
public:
    double elem[3][3];

public:
    void Set(double, double, double,
             double, double, double,
             double, double, double);

    void Print();

    DCM operator+(const DCM other) const;
    DCM operator*(const DCM other) const;
    Vect operator*(const Vect v) const;
    DCM operator*(const double d) const;
    DCM Transpose();
    double *operator[](const int index);
    void operator=(const DCM &other);
};

DCM Euler2DCM(double x, double y, double z);
double sind(double x);
double cosd(double x);
double atan2d(double x, double y);