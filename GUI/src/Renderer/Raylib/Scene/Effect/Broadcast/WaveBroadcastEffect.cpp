/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** WaveBroadcastEffect.cpp
*/

#include "WaveBroadcastEffect.hpp"

zappy::gui::raylib::WaveBroadcastEffect::WaveBroadcastEffect(const int &playerId, const float &duration, const Color &color) :
    ABroadcastEffect(playerId, duration, color),
    _pulseTimer(0.f)
{}

void zappy::gui::raylib::WaveBroadcastEffect::update(const float &deltaUnits)
{
    AEffect::update(deltaUnits);

    _pulseTimer += deltaUnits;

    if (_elapsedTime <= _duration && _pulseTimer >= PULSE_INTERVAL) {
        _pulses.push_back(Pulse{0.0f, 0.0f});
        _pulseTimer = 0.0f;
    }

    for (auto &pulse : _pulses)
        pulse.elapsed += deltaUnits;

    _pulses.erase(
        std::remove_if(_pulses.begin(), _pulses.end(),
            [](const Pulse &p) {
                return p.elapsed >= PULSE_LIFETIME;
            }),
        _pulses.end()
    );
}

bool zappy::gui::raylib::WaveBroadcastEffect::hasEnded() const
{
    return ABroadcastEffect::hasEnded() && _pulses.empty();
}

void zappy::gui::raylib::WaveBroadcastEffect::render(const Vector3 &position) const
{
    // Décalage vertical (par exemple : 0.5f au-dessus du joueur)
    Vector3 elevatedPos = position;
    elevatedPos.y += 0.5f;

    for (const auto &pulse : _pulses) {
        float radius = pulse.elapsed * PULSE_SPEED * 2.5f; // plus grand
        float alpha  = 1.0f - (pulse.elapsed / PULSE_LIFETIME);

        Color faded = _color;
        faded.a = static_cast<unsigned char>(255 * alpha);

        DrawCircle3D(
            elevatedPos,
            radius,
            {1, 0, 0},
            90.0f,
            faded
        );
    }
}
