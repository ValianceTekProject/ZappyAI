/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Broadcast.cpp
*/

#include "AEffect.hpp"

zappy::gui::raylib::AEffect::AEffect(
    const int &playerId,
    const float &duration,
    const Color &color
) :
    _playerId(playerId),
    _elapsedTime(0),
    _duration(duration),
    _color(color)
{}

void zappy::gui::raylib::AEffect::update(const float &deltaUnits)
{
    this->_elapsedTime += deltaUnits;
}

bool zappy::gui::raylib::AEffect::hasEnded() const
{
    return this->_elapsedTime >= this->_duration;
}
