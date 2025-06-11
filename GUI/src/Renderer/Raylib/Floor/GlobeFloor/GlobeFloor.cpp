/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** GlobeFloor.cpp
*/

#include "GlobeFloor.hpp"

zappy::gui::raylib::GlobeFloor::GlobeFloor()
    : AFloor() {}

void zappy::gui::raylib::GlobeFloor::draw(const Map &map) const
{
    int gridSize = getGridSize();
    int spacing = getSpacing();

    for (int x = 0; x < map.getWidth(); ++x) {
        for (int y = 0; y < map.getHeight(); ++y) {
            Vector2 position = { static_cast<float>(x * (gridSize + spacing)),
                                 static_cast<float>(y * (gridSize + spacing)) };
            DrawCircleV(position, static_cast<float>(gridSize / 2), DARKGRAY);
        }
    }
}