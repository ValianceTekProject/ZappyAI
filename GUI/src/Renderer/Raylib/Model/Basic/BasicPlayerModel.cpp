/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** BasicPlayerModel.cpp
*/

#include "BasicPlayerModel.hpp"

#include <raylib.h>
#include <stdio.h>

zappy::gui::raylib::BasicPlayerModel::BasicPlayerModel(const int &id) :
    APlayerModel::APlayerModel(id)
{
    constexpr float scale = 0.15;
    setScale(scale);
}

void zappy::gui::raylib::BasicPlayerModel::init()
{
    APlayerModel::init();

    APlayerModel::_initModel(assets::BASIC_PLAYER_PATH);

    rotate({0, 180, 0});
}

void zappy::gui::raylib::BasicPlayerModel::update()
{
    APlayerModel::update();
}
