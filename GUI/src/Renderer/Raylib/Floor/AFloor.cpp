/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** AFloor.cpp
*/

#include "AFloor.hpp"

// Setters
void zappy::gui::raylib::AFloor::setSpacing(int spacing)
{
    _spacing = spacing;
}

void zappy::gui::raylib::AFloor::setWidth(int width)
{
    _width = width;
}

void zappy::gui::raylib::AFloor::setHeight(int height)
{
    _height = height;
}

// Getters
int zappy::gui::raylib::AFloor::getSpacing() const
{
    return _spacing;
}

int zappy::gui::raylib::AFloor::getWidth() const
{
    return _width;
}

int zappy::gui::raylib::AFloor::getHeight() const
{
    return _height;
}

void zappy::gui::raylib::AFloor::draw() const {}
