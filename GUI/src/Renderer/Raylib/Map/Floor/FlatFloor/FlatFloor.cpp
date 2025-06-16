/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** FlatFloor.cpp
*/

#include "FlatFloor.hpp"
#include "raylib.h"
#include <algorithm>

zappy::gui::raylib::FlatFloor::FlatFloor(size_t width, size_t height, size_t tileSize) :
    AFloor::AFloor(width, height, tileSize)
{}

void zappy::gui::raylib::FlatFloor::init()
{
    AFloor::init();
}

void zappy::gui::raylib::FlatFloor::render() const
{
    size_t tileSize = getTileSize();

    float gridWidth = getWidth() * tileSize;
    float gridHeight = getHeight() * tileSize;

    float startX = -gridWidth / 2.0f;
    float startZ = -gridHeight / 2.0f;
    float endX = gridWidth / 2.0f;
    float endZ = gridHeight / 2.0f;

    for (size_t i = 0; i <= getWidth(); i++) {
        float x = startX + i * tileSize;
        Vector3 start = {x, 0.0f, startZ};
        Vector3 end = {x, 0.0f, endZ};
        DrawLine3D(start, end, GRAY);
    }

    for (size_t j = 0; j <= getHeight(); j++) {
        float z = startZ + j * tileSize;
        Vector3 start = {startX, 0.0f, z};
        Vector3 end = {endX, 0.0f, z};
        DrawLine3D(start, end, GRAY);
    }
}
