/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** ARenderer.cpp
*/

#include "ARenderer.hpp"

void zappy::gui::ARenderer::addEgg(
    const int &eggId,
    const int &fatherId,
    const int &x,
    const int &y
) {
    _checkGameState();
    _gameState->addEgg(eggId, fatherId, x, y);
}

void zappy::gui::ARenderer::addPlayer(const game::Player &player)
{
    _checkGameState();
    _gameState->addPlayer(player);
}

void zappy::gui::ARenderer::updatePlayerPosition(
    const int &id,
    const int &x,
    const int &y,
    const game::Orientation &orientation
) {
    _checkGameState();
    _gameState->updatePlayerPosition(id, x, y, orientation);
}

void zappy::gui::ARenderer::updatePlayerLevel(const int &id, const size_t &level)
{
    _checkGameState();
    _gameState->updatePlayerLevel(id, level);
}

void zappy::gui::ARenderer::updatePlayerInventory(const int &id, const game::Inventory &inventory)
{
    _checkGameState();
    _gameState->updatePlayerInventory(id, inventory);
}

void zappy::gui::ARenderer::PlayerExpulsion(const int &id)
{
    _checkGameState();
    _gameState->PlayerExpulsion(id);
}

void zappy::gui::ARenderer::PlayerBroadcast(const int &id, const std::string &message)
{
    _checkGameState();
    _gameState->PlayerBroadcast(id, message);
}

void zappy::gui::ARenderer::StartIncantation(
    const int &x, const int &y,
    const int &level,
    const std::vector<int> &playerIds
) {
    _checkGameState();
    _gameState->StartIncantation(x, y, level, playerIds);
}

void zappy::gui::ARenderer::EndIncantation(const int &x, const int &y, const bool &result)
{
    _checkGameState();
    _gameState->EndIncantation(x, y, result);
}

void zappy::gui::ARenderer::hatchEgg(const int &eggId)
{
    _checkGameState();
    _gameState->hatchEgg(eggId);
}

void zappy::gui::ARenderer::removeEgg(const int &eggId)
{
    _checkGameState();
    _gameState->removeEgg(eggId);
}

void zappy::gui::ARenderer::removePlayer(const int &id)
{
    _checkGameState();
    _gameState->removePlayer(id);
}

void zappy::gui::ARenderer::endGame(const std::string &teamName)
{
    _checkGameState();
    _gameState->endGame(teamName);
}

void zappy::gui::ARenderer::_checkGameState() const
{
    if (!_gameState)
        throw GuiError("Game state is not set", "ARenderer");
}
