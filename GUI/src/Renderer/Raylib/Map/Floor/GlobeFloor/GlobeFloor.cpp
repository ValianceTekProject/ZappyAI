/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** GlobeFloor.cpp
*/

#include "GlobeFloor.hpp"
#include <math.h>

zappy::gui::raylib::GlobeFloor::GlobeFloor(const zappy::game::Map &map, int radius)
    : AFloor(map), _radius(radius) {}

void zappy::gui::raylib::GlobeFloor::draw() const
{
    int numLatitudeDivisions = std::max(4, (int)(M_PI * _radius / getSpacing()));
    int numLongitudeDivisions = std::max(8, (int)(2 * M_PI * _radius / getSpacing()));
    
    auto getPointOnSphere = [this](float theta, float phi) -> Vector3 {
        return Vector3{
            _radius * sin(theta) * cos(phi),
            _radius * cos(theta),
            _radius * sin(theta) * sin(phi)
        };
    };
    
    for (int i = 0; i < numLatitudeDivisions; i++) {
        for (int j = 0; j < numLongitudeDivisions; j++) {
            float theta1 = M_PI * i / numLatitudeDivisions;
            float theta2 = M_PI * (i + 1) / numLatitudeDivisions;
            float phi1 = 2 * M_PI * j / numLongitudeDivisions;
            float phi2 = 2 * M_PI * (j + 1) / numLongitudeDivisions;
            
            Vector3 topLeft = getPointOnSphere(theta1, phi1);
            Vector3 topRight = getPointOnSphere(theta1, phi2);
            Vector3 bottomLeft = getPointOnSphere(theta2, phi1);
            Vector3 bottomRight = getPointOnSphere(theta2, phi2);
            
            DrawLine3D(topLeft, topRight, BLUE);
            DrawLine3D(topRight, bottomRight, BLUE);
            DrawLine3D(bottomRight, bottomLeft, BLUE);
            DrawLine3D(bottomLeft, topLeft, BLUE);
        }
    }
}