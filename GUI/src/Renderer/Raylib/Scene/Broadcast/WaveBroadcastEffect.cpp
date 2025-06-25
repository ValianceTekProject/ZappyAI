/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** WaveBroadcastEffect.cpp
*/

#include "WaveBroadcastEffect.hpp"

zappy::gui::raylib::WaveBroadcastEffect::WaveBroadcastEffect(
    const int &playerId,
    const float &duration,
    const Color &color
) :
    ABroadcastEffect(playerId, duration, color),
    _radius(0)
{}

void zappy::gui::raylib::WaveBroadcastEffect::update(const float &deltaUnits)
{
    this->_elapsedTime += deltaUnits;
    this->_radius += deltaUnits * 10;
}

void zappy::gui::raylib::WaveBroadcastEffect::render() const
{
    DrawCircle(0, 0, this->_radius, WHITE);
}
