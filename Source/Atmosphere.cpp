#include "Lightweaver.hpp"
#include "Constants.hpp"
#include <cmath>

void Atmosphere::update_projections()
{
    switch (Ndim)
    {
        case 1:
        {
            for (int mu = 0; mu < Nrays; ++mu)
            {
                for (int toObsI = 0; toObsI < 2; ++toObsI)
                {
                    for (int k = 0; k < Nspace; ++k)
                    {
                        vlosMu(mu, toObsI, k) = muz(mu,toObsI) * vz(k);
                    }
                }
            }
        } break;

        case 2:
        {
            for (int mu = 0; mu < Nrays; ++mu)
            {
                for (int toObsI = 0; toObsI < 2; ++toObsI)
                {
                    for (int k = 0; k < Nspace; ++k)
                    {
                        vlosMu(mu, toObsI, k) = mux(mu,toObsI) * vx(k) + muz(mu,toObsI) * vz(k);
                    }
                }
            }
        } break;

        case 3:
        {
            for (int mu = 0; mu < Nrays; ++mu)
            {
                for (int toObsI = 0; toObsI < 2; ++toObsI)
                {
                    for (int k = 0; k < Nspace; ++k)
                    {
                        vlosMu(mu, toObsI, k) = mux(mu,toObsI) * vx(k) + muy(mu,toObsI) * vy(k) + muz(mu,toObsI) * vz(k);
                    }
                }
            }
        } break;

        default:
        {
        } break;
    }

    if (!B)
        return;

    for (int mu = 0; mu < Nrays; ++mu)
    {
        for (int toObsI = 0; toObsI < 2; ++toObsI)
        {
            if (muz(mu,toObsI) == 1.0)
            {
                for (int k = 0; k < Nspace; ++k)
                {
                    cosGamma(mu, toObsI, k) = cos(gammaB(k));
                    cos2chi(mu, toObsI, k)  = cos(2.0 * chiB(k));
                    sin2chi(mu, toObsI, k)  = sin(2.0 * chiB(k));
                }
            }
            else
            {
                f64 cscTheta = 1.0 / sqrt(1.0 - square(muz(mu,toObsI)));
                for (int k = 0; k < Nspace; ++k)
                {
                    // NOTE(cmo): Basic projection using spherical polar
                    // coordinates.
                    f64 sinGamma = sin(gammaB(k));
                    f64 bx = sinGamma * cos(chiB(k));
                    f64 by = sinGamma * sin(chiB(k));
                    f64 bz = cos(gammaB(k));

                    f64 b3 = mux(mu, toObsI)*bx + muy(mu, toObsI)*by + muz(mu, toObsI)*bz;
                    f64 b1 = cscTheta * (bz - muz(mu, toObsI)*b3);
                    f64 b2 = cscTheta * (muy(mu, toObsI)*bx - mux(mu, toObsI)*by);

                    cosGamma(mu, toObsI, k) = b3;
                    cos2chi(mu, toObsI, k)  = (square(b1) - square(b2)) / (1.0 - square(b3));
                    sin2chi(mu, toObsI, k)  = 2.0 * b1*b2 / (1.0 - square(b3));
                }
            }
        }
    }

}