/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Broadcast.cpp
*/

#include "ABroadcastEffect.hpp"

zappy::gui::raylib::ABroadcastEffect::ABroadcastEffect(
    const int &playerId,
    const float &duration,
    const Color &color
) :
    _playerId(playerId),
    _elapsedTime(0),
    _duration(duration),
    _color(color)
{}

void zappy::gui::raylib::ABroadcastEffect::update(const float &deltaUnits)
{
    this->_elapsedTime += deltaUnits;
}

bool zappy::gui::raylib::ABroadcastEffect::isFinished() const
{
    return this->_elapsedTime >= this->_duration;
}
