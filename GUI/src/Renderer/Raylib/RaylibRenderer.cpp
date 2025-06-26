/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** RaylibRenderer.cpp
*/

#include "RaylibRenderer.hpp"

zappy::gui::RaylibRenderer::RaylibRenderer() :
    ARenderer::ARenderer(),
    _scene(nullptr)
{
    SetTraceLogLevel(LOG_NONE);
}

void zappy::gui::RaylibRenderer::init()
{
    // Initialisation Raylib ici
    InitWindow(1280, 720, "Zappy");
    // ToggleFullscreen();
    SetTargetFPS(60);
    DisableCursor();

    _scene = std::make_unique<raylib::BasicScene>(_gameState);
    _scene->init();

    constexpr int id = 0;
    game::Player p(id, 0, 9);
    this->addPlayer(p);
    this->updatePlayerPosition(0, 0, 8, game::Orientation::NORTH);
    this->updatePlayerPosition(0, 0, 8, game::Orientation::EAST);
    this->playerBroadcast(id, "là là là");
    this->updatePlayerPosition(0, 1, 8, game::Orientation::EAST);
}

void zappy::gui::RaylibRenderer::handleInput()
{
    _inputManager.update();
    _scene->handleInput(_inputManager);
}

void zappy::gui::RaylibRenderer::update()
{
    _scene->update();
}

void zappy::gui::RaylibRenderer::render() const
{
    UpdateCamera(&_scene->getCamera(), CAMERA_FREE);

    BeginDrawing();
    ClearBackground(SKYBLUE);

    _scene->render();

    EndDrawing();
}

bool zappy::gui::RaylibRenderer::shouldClose() const
{
    return WindowShouldClose();
}

void zappy::gui::RaylibRenderer::addEgg(const int &eggId,
    const int &fatherId,
    const int &x,
    const int &y
) {
    ARenderer::addEgg(eggId, fatherId, x, y);
    _scene->addEgg(eggId);
}

void zappy::gui::RaylibRenderer::addPlayer(const game::Player &player)
{
    ARenderer::addPlayer(player);
    _scene->addPlayer(player.getId());
}

void zappy::gui::RaylibRenderer::updatePlayerPosition(const int &id,
    const int &x,
    const int &y,
    const game::Orientation &orientation
) {
    _scene->updatePlayerPosition(id, x, y, orientation);
    ARenderer::updatePlayerPosition(id, x, y, orientation);
}

void zappy::gui::RaylibRenderer::updatePlayerLevel(const int &id, const size_t &level)
{
    _scene->updatePlayerLevel(id, level);
    ARenderer::updatePlayerLevel(id, level);
}

void zappy::gui::RaylibRenderer::updatePlayerInventory(const int &id, const game::Inventory &inventory)
{
    _scene->updatePlayerInventory(id, inventory);
    ARenderer::updatePlayerInventory(id, inventory);
}

void zappy::gui::RaylibRenderer::playerExpulsion(const int &id)
{
    _scene->playerExpulsion(id);
    ARenderer::playerExpulsion(id);
}

void zappy::gui::RaylibRenderer::playerBroadcast(const int &id, const std::string &message)
{
    ARenderer::playerBroadcast(id, message);
    _scene->playerBroadcast(id, message);
}

void zappy::gui::RaylibRenderer::startIncantation(
    const int &x, const int &y,
    const int &level,
    const std::vector<int> &playerIds
) {
    ARenderer::startIncantation(x, y, level, playerIds);
    _scene->startIncantation(x, y, level, playerIds);
}

void zappy::gui::RaylibRenderer::endIncantation(const int &x, const int &y, const bool &result)
{
    ARenderer::endIncantation(x, y, result);
    _scene->endIncantation(x, y, result);
}

void zappy::gui::RaylibRenderer::hatchEgg(const int &eggId)
{
    ARenderer::hatchEgg(eggId);
    _scene->hatchEgg(eggId);
}

void zappy::gui::RaylibRenderer::removeEgg(const int &eggId)
{
    ARenderer::removeEgg(eggId);
    _scene->removeEgg(eggId);
}

void zappy::gui::RaylibRenderer::removePlayer(const int &id)
{
    ARenderer::removePlayer(id);
    _scene->removePlayer(id);
}

void zappy::gui::RaylibRenderer::endGame(const std::string &teamName)
{
    ARenderer::endGame(teamName);
    _scene->endGame(teamName);
}
