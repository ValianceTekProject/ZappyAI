/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** FlatFloor.cpp
*/

#include "FlatFloor.hpp"
#include "raylib.h"

zappy::gui::raylib::FlatFloor::FlatFloor()
    : AFloor() {}

void zappy::gui::raylib::FlatFloor::draw(const Map &map) const
{
    int gridSize = getGridSize();
    int spacing = getSpacing();

    for (int x = 0; x < map.getWidth(); ++x) {
        for (int y = 0; y < map.getHeight(); ++y) {
            Vector2 position = { static_cast<float>(x * (gridSize + spacing)),
                                 static_cast<float>(y * (gridSize + spacing)) };
            DrawRectangleV(position, { static_cast<float>(gridSize), static_cast<float>(gridSize) }, DARKGRAY);
        }
    }
}