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

    constexpr int idle = 0;
    constexpr int open = 2;

    this->_animationIndexMap[State::IDLE] = idle;
    this->_animationIndexMap[State::OPEN] = open;

    constexpr float idleSpeed = 7.5f;
    constexpr float openSpeed = 7.5f;

    this->_animationFrameSpeedMap[State::IDLE] = idleSpeed;
    this->_animationFrameSpeedMap[State::OPEN] = openSpeed;
}
