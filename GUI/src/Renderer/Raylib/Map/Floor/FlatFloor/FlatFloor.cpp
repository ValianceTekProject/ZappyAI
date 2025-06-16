/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** FlatFloor.cpp
*/

#include "FlatFloor.hpp"
#include "raylib.h"
#include <algorithm>

zappy::gui::raylib::FlatFloor::FlatFloor(const zappy::game::Map &map)
    : AFloor(map)
{
    setWidth(static_cast<int>(map.getWidth()));
    setHeight(static_cast<int>(map.getHeight()));
}

void zappy::gui::raylib::FlatFloor::draw() const
{
    float gridWidth = getWidth() * getSpacing();
    float gridHeight = getHeight() * getSpacing();
    
    float startX = -gridWidth / 2.0f;
    float startZ = -gridHeight / 2.0f;
    float endX = gridWidth / 2.0f;
    float endZ = gridHeight / 2.0f;
    
    for (int i = 0; i <= getWidth(); i++) {
        float x = startX + i * getSpacing();
        Vector3 start = {x, 0.0f, startZ};
        Vector3 end = {x, 0.0f, endZ};
        DrawLine3D(start, end, GRAY);
    }
    
    for (int j = 0; j <= getHeight(); j++) {
        float z = startZ + j * getSpacing();
        Vector3 start = {startX, 0.0f, z};
        Vector3 end = {endX, 0.0f, z};
        DrawLine3D(start, end, GRAY);
    }
}
