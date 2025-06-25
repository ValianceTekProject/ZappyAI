/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** Incantation.cpp
*/

#include "Incantation.hpp"
#include <cmath>

zappy::gui::raylib::Incantation::Incantation(Vector2 tile) : _tile(tile), _animationTime(0.f) {}

void zappy::gui::raylib::Incantation::update(float deltaTime)
{
    _animationTime += deltaTime;
    if (_animationTime > 3.0f)
        _animationTime -= 3.0f;
}

void zappy::gui::raylib::Incantation::render(class IFloor *floor) const
{
    Vector3 tilePos = floor->get3DCoords(static_cast<int>(_tile.x), static_cast<int>(_tile.y));
    float progress = _animationTime / 3.0f;

    _renderSpiralParticles(tilePos, progress);
}

void zappy::gui::raylib::Incantation::_renderSpiralParticles(const Vector3& center, float progress) const
{
    int numParticles = 200;
    for (int i = 0; i < numParticles; i++) {
        float particleProgress = fmod(progress + i / (float)numParticles, 1.0f);
        float angle = particleProgress * 4 * PI + i * PI / 6;
        float height = particleProgress * 1.5f;
        float radius = 0.4f * (1.0f - particleProgress * 0.5f);

        Vector3 particlePos = center;
        particlePos.x += cos(angle) * radius;
        particlePos.z += sin(angle) * radius;
        particlePos.y += height;

        unsigned char alpha = static_cast<unsigned char>(255 * (1.0f - particleProgress));
        Color particleColor = {
            150,
            200,
            255,
            alpha
        };

        float particleSize = 0.025f;
        DrawSphere(particlePos, particleSize, particleColor);
    }
}

bool zappy::gui::raylib::Incantation::isAt(int x, int y) const
{
    return static_cast<int>(_tile.x) == x && static_cast<int>(_tile.y) == y;
}