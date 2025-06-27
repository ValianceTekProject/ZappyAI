/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** SpiralIncantationEffect.cpp
*/

#include "SpiralIncantationEffect.hpp"

zappy::gui::raylib::SpiralIncantationEffect::SpiralIncantationEffect(const int &playerId, const float &duration, const Color &color) :
    AIncantationEffect(playerId, duration, color) {}

void zappy::gui::raylib::SpiralIncantationEffect::update(const float &deltaUnits)
{
    AEffect::update(deltaUnits);

    _animationTime += deltaUnits;
    if (_animationTime > 3.0f)
        _animationTime -= 3.0f;
}

void zappy::gui::raylib::SpiralIncantationEffect::render(const Vector3 &position) const
{
    float progress = _animationTime / 3.0f;

    _renderSpiralParticles(position, progress);
}

void zappy::gui::raylib::SpiralIncantationEffect::_renderSpiralParticles(const Vector3& center, float progress) const
{
    constexpr int numParticles = 200;
    constexpr float particleSize = 0.025f;
    for (int i = 0; i < numParticles; i++) {
        float particleProgress = fmod(progress + i / (float)numParticles, 1.0f);
        float angle = particleProgress * 4 * PI + i * PI / 6;
        float height = particleProgress * 1.5f;
        float radius = 0.4f * (1.0f - particleProgress * 0.5f);

        Vector3 particlePos = center;
        particlePos.x += cos(angle) * radius;
        particlePos.z += sin(angle) * radius;
        particlePos.y += height;

        DrawSphere(particlePos, particleSize, _color);
    }
}

bool zappy::gui::raylib::SpiralIncantationEffect::isAt(int x, int y) const
{
    return static_cast<int>(_tile.x) == x && static_cast<int>(_tile.y) == y;
}
