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
    ABroadcastEffect(playerId, duration, color)
{
    constexpr float defaultRadius = 0;
    this->_radius = defaultRadius;
}

void zappy::gui::raylib::WaveBroadcastEffect::update(const float &deltaUnits)
{
    ABroadcastEffect::update(deltaUnits);

    float progress = _elapsedTime / _duration;
    _radius = progress * 10.0f;
}

void zappy::gui::raylib::WaveBroadcastEffect::render(const Vector3 &position) const
{
    if (_elapsedTime >= _duration)
        return;

    float alpha = 1.0f - (_elapsedTime / _duration);
    Color fadedColor = _color;
    fadedColor.a = static_cast<unsigned char>(255 * alpha);

    DrawCircle3D(
        position,
        _radius,
        Vector3{1, 0, 0},
        90.0f,
        fadedColor
    );
}
