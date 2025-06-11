/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** AFloor.cpp
*/

#include "AFloor.hpp"

zappy::gui::raylib::AFloor::AFloor()
    : gridSize(10), spacing(5) {}

// Setters
void zappy::gui::raylib::AFloor::setGridSize(int size)
{
    gridSize = size;
}

void zappy::gui::raylib::AFloor::setSpacing(int spacing)
{
    this->spacing = spacing;
}

// Getters
int zappy::gui::raylib::AFloor::getGridSize() const
{
    return gridSize;
}

int zappy::gui::raylib::AFloor::getSpacing() const
{
    return spacing;
}
