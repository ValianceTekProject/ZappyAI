/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** PlayerBroadcast.cpp
*/

#include "PlayerIncantation.hpp"

zappy::gui::raylib::PlayerIncantation::PlayerIncantation(
    const int &playerId,
    const ActionType &type,
    std::unique_ptr<IIncantationEffect> effect,
    const float &timeUnit,
    const float &elapsedTime
) :
    APlayerAction(playerId, type, timeUnit, elapsedTime),
    _effect(std::move(effect))
{}

void zappy::gui::raylib::PlayerIncantation::update(const float &deltaUnits, APlayerModel &player)
{
    if (this->_effect)
        this->_effect->update(deltaUnits);
    APlayerAction::update(deltaUnits, player);
}

void zappy::gui::raylib::PlayerIncantation::finishAction(APlayerModel &player)
{
    (void)player;
    this->_effect.reset();
}

void zappy::gui::raylib::PlayerIncantation::render(const Vector3 &position)
{
    if (this->_effect)
        this->_effect->render(position);
}
