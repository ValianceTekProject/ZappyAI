/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** PlayerBroadcast.cpp
*/

#include "PlayerBroadcast.hpp"

zappy::gui::raylib::PlayerBroadcast::PlayerBroadcast(
    const int &playerId,
    const ActionType &type,
    std::unique_ptr<IBroadcastEffect> effect,
    const float &timeUnit,
    const float &elapsedTime
) :
    APlayerAction(playerId, type, timeUnit, elapsedTime),
    _effect(std::move(effect))
{}

void zappy::gui::raylib::PlayerBroadcast::update(const float &deltaUnits, APlayerModel &player)
{
    if (this->_effect)
        this->_effect->update(deltaUnits);
    APlayerAction::update(deltaUnits, player);
}

void zappy::gui::raylib::PlayerBroadcast::finishAction(APlayerModel &player)
{
    (void)player;
    this->_effect.reset();
}

void zappy::gui::raylib::PlayerBroadcast::render(const Vector3 &position)
{
    if (this->_effect)
        this->_effect->render(position);
}
