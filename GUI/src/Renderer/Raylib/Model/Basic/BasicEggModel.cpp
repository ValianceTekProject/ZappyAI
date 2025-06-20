/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** BasicEggModel.cpp
*/

#include "BasicEggModel.hpp"

#include <raylib.h>
#include <stdio.h>

zappy::gui::raylib::BasicEggModel::BasicEggModel(const int &id) : AEggModel::AEggModel(id)
{
    constexpr float scale = 0.1;
    setScale(scale);
}

void zappy::gui::raylib::BasicEggModel::init()
{
    AEggModel::init();

    AEggModel::_initModel(assets::BASIC_EGG_PATH);
}

void zappy::gui::raylib::BasicEggModel::update()
{
    AEggModel::update();
}
