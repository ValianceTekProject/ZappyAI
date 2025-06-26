/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** AIncantationEffect.cpp
*/

#include "AIncantationEffect.hpp"

zappy::gui::raylib::AIncantationEffect::AIncantationEffect(
    const int &playerId,
    const float &duration,
    const Color &color
) :
    _playerId(playerId),
    _elapsedTime(0),
    _duration(duration),
    _color(color)
{}

void zappy::gui::raylib::AIncantationEffect::update(const float &deltaUnits)
{
    this->_elapsedTime += deltaUnits;
}

bool zappy::gui::raylib::AIncantationEffect::isFinished() const
{
    return this->_elapsedTime >= this->_duration;
}
