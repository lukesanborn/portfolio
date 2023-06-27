#include "PoseMatrix.h"
#include <stdio.h>

// matrix indices: 
// 00  01  02
// 10  11  12
// 20  21  22


/**
 * @brief converts euler angles to direction cosine matrix
 * 
 * @param x phi angle
 * @param y theta angle
 * @param z psi angle
 * @return DCM 
 */
DCM Euler2DCM(double x, double y, double z)
{
    DCM cx, cy, cz;
    DCM res;

    cx[0][0] = 1.0;      cx[0][1] = 0.0;      cx[0][2] = 0.0;
    cx[1][0] = 0.0;      cx[1][1] = cosd(x);   cx[1][2] = sind(x);
    cx[2][0] = 0.0;      cx[2][1] = -sind(x);  cx[2][2] = cosd(x);

    cy[0][0] = cosd(y);   cy[0][1] = 0.0;      cy[0][2] = -sind(y);
    cy[1][0] = 0.0;      cy[1][1] = 1.0;      cy[1][2] = 0.0;
    cy[2][0] = sind(y);   cy[2][1] = 0.0;      cy[2][2] = cosd(y);

    cz[0][0] = cosd(z);   cz[0][1] = sind(z);   cz[0][2] = 0.0;
    cz[1][0] = -sind(z);  cz[1][1] = cosd(z);   cz[1][2] = 0.0;
    cz[2][0] = 0.0;      cz[2][1] = 0.0;      cz[2][2] = 1.0;

    DCM temp = cx*cy;
    res = temp*cz;

    return res;
}


/**
 * @brief Set values in a vector
 * 
 * @param elem0 first element
 * @param elem1 second element
 * @param elem2 thirds
 */
void Vect::Set(double elem0 = 0, double elem1 = 0, double elem2 = 0)
{
elem[0] = elem0; elem[1] = elem1; elem[2] = elem2;
}

/**
 * @brief Print values
 * 
 */
void Vect::Print()
{
    for (int i = 0; i < 3; i++)
    {
        printf("%f\n", elem[i]);
    }
}

/**
 * @brief overloaded operator for adding a vector and a vector
 * 
 * @param other other vector addent
 * @return Vect 
 */
Vect Vect::operator +(const Vect other) const
{
    Vect res;
    for (int i = 0; i < 3; i++)
    {
        res.elem[i] = elem[i] + other.elem[i];
    }
    return res; 
}

/**
 * @brief overloaded operator for multiplying a vector and a double
 * 
 * @param d double factor 
 * @return Vect 
 */
Vect Vect::operator *(const double d) const
{
    Vect res;
    for (int i = 0; i < 3; i++)
    {
        res.elem[i] = elem[i]*d;
    }
    return res;
}

/**
 * @brief unary -, sign change for vector elements
 * 
 * @return Vect 
 */
Vect Vect::operator -() const
{
    Vect res;
    for (int i = 0; i < 3; i++)
    {
        res.elem[i] = -elem[i];
    }
    return res;
}
/**
 * @brief Accessor for vect
 * 
 * @param index 
 * @return double& 
 */
double &Vect::operator[](const int index) 
{
    return elem[index];
}
/**
 * @brief Check equality
 * 
 * @param other 
 */
void Vect::operator =(const Vect &other)
{
    if (elem != other.elem)
    {
        for(int i = 0; i < 3; i++)
        {
            elem[i] = other.elem[i];
        }
    }
}



/**
 * @brief Set values for a Direction Cosine Matrix
 * 
 * @param elem00 
 * @param elem01 
 * @param elem02 
 * @param elem10 
 * @param elem11 
 * @param elem12 
 * @param elem20 
 * @param elem21 
 * @param elem22 
 */
void DCM::Set(double elem00 = 0, double elem01 = 0, double elem02 = 0,
double elem10 = 0, double elem11 = 0, double elem12 = 0,
double elem20 = 0, double elem21 = 0, double elem22 = 0)
{
elem[0][0] = elem00; elem[0][1] = elem01; elem[0][2] = elem02;
elem[1][0] = elem10; elem[1][1] = elem11; elem[1][2] = elem12;
elem[2][0] = elem20; elem[2][1] = elem21; elem[2][2] = elem22;
}
/**
 * @brief Print values in a DCM
 * 
 */
void DCM::Print()
{
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            printf("%2f ", elem[i][j]);
        }
        printf("\n");
    } 
}

/**
 * @brief overloaded operator for adding a DCM and a DCM
 * 
 * @param other other DCM addent
 * @return DCM 
 */
DCM DCM::operator +(const DCM other) const
{
    DCM res;
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            res[i][j] = elem[i][j] + other.elem[i][j];
        }
    }
    return res;
}

/**
 * @brief multiplies two direction cosine matrices
 * 
 * @param a first direction cosine matrix (3, 3)
 * @param b second direction cosine matrix (3, 3)
 * @return DCM 
 */
DCM DCM::operator *(const DCM other)const
{
    DCM res;
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            res[i][j] = elem[i][0]*other.elem[0][j] + elem[i][1]*other.elem[1][j] + elem[i][2]*other.elem[2][j];
        }
    }
    return res;
}

/**
 * @brief multiplies a direction cosine matrix and a vector
 * 
 * @param a 
 * @param v 
 * @return DCM 
 */
Vect DCM::operator *(Vect v) const
{
    Vect res;
    for (int i = 0; i < 3; i++)
    {
        res[i] = elem[i][0]*v[0] + elem[i][1]*v[1] + elem[i][2]*v[2];
    }
    return res;
}

/**
 * @brief transposes a direction cosine matrix
 * 
 * @param a direction cosine matrix (3, 3)
 * @return DCM 
 */
DCM DCM::Transpose()
{
    DCM res;
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            res[i][j] = elem[j][i];
        }
    }
    return res;
}

/**
 * @brief overloaded operator for multiplying a DCM and a double
 * 
 * @param d double factor
 * @return DCM 
 */
DCM DCM::operator *(const double d)const
{
    DCM res;
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            res[i][j] = elem[i][j]*d;
        }
    }
    return res;
}
/**
 * @brief Accessor function for swerve
 * 
 * @param index 
 * @return double* 
 */
double *DCM::operator[](const int index) 
{
    return elem[index];
}

/**
 * @brief Check equality
 * 
 * @param other 
 */
void DCM::operator =(const DCM &other)
{
    if(elem != other.elem)
    {
        for (int i = 0; i < 3; i++)
        {
            for (int j = 0; j < 3; j++)
            {
                elem[i][j] = other.elem[i][j];
            }
        }
    }
}
/**
 * @brief Sin of an angle in degrees
 * 
 * @param x value in degrees
 * @return double 
 */
double sind(double x)
{
    return sin(x * (M_PI / 180.0));
}
/**
 * @brief Cosine of an angle in degrees
 * 
 * @param x value in degrees
 * @return double 
 */
double cosd(double x)
{
    return cos(x * (M_PI / 180.0));
}
/**
 * @brief Arctan of sides
 * 
 * @param x base 1
 * @param y base 2
 * @return double angle in degrees
 */
double atan2d(double x, double y)
{
    return atan2(x, y) * (180.0 / M_PI);
}