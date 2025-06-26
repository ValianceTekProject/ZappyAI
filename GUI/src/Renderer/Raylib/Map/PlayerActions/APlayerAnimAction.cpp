/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** PlayerBroadcast.cpp
*/

#include "PlayerBroadcast.hpp"

zappy::gui::raylib::APlayerAnimAction::APlayerAnimAction(
    const int &animationid,
    const int &playerId,
    const ActionType &type,
    std::unique_ptr<IEffect> effect,
    const float &timeUnit,
    const float &elapsedTime
) :
    APlayerAction(playerId, type, timeUnit, elapsedTime),
    _effect(std::move(effect)),
    _animationid(animationid) {}

void zappy::gui::raylib::APlayerAnimAction::update(const float &deltaUnits, APlayerModel &player)
{
    if (this->_effect)
        this->_effect->update(deltaUnits);
    APlayerAction::update(deltaUnits, player);
}

void zappy::gui::raylib::APlayerAnimAction::render(const Vector3 &position)
{
    if (this->_effect)
        this->_effect->render(position);
}
