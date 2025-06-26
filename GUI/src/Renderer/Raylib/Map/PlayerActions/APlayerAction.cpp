/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** APlayerAction.cpp
*/

#include "APlayerAction.hpp"

zappy::gui::raylib::APlayerAction::APlayerAction(
    const int &playerId,
    const ActionType &actionType,
    const float &timeUnit,
    const float &elapsedTime
) :
    playerId(playerId),
    actionType(actionType),
    _timeUnit(timeUnit),
    _elapsedTime(elapsedTime),
    _hasStarted(false)
{}

void zappy::gui::raylib::APlayerAction::update(const float &deltaUnits, APlayerModel &player)
{
    (void)player;
    this->_elapsedTime += deltaUnits;
}

bool zappy::gui::raylib::APlayerAction::ActionWillEnd(const float &deltaUnits) const
{
    return this->_elapsedTime + deltaUnits >= this->_timeUnit;
}

void zappy::gui::raylib::APlayerAction::finishAction(const float &deltaUnits, APlayerModel &player)
{
    update(deltaUnits, player);
}
