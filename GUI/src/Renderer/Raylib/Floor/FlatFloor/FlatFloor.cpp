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
   DrawGrid(std::max(getWidth(), getHeight()), static_cast<float>(getSpacing()));
}
