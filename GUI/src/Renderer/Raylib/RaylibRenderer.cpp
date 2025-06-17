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
}

void zappy::gui::RaylibRenderer::addPlayer(const game::Player &player)
{
    ARenderer::addPlayer(player);
}

void zappy::gui::RaylibRenderer::updatePlayerPosition(const int &id,
    const int &x,
    const int &y,
    const game::Orientation &orientation
) {
    ARenderer::updatePlayerPosition(id, x, y, orientation);
}

void zappy::gui::RaylibRenderer::updatePlayerLevel(const int &id, const size_t &level)
{
    ARenderer::updatePlayerLevel(id, level);
}

void zappy::gui::RaylibRenderer::updatePlayerInventory(const int &id, const game::Inventory &inventory)
{
    ARenderer::updatePlayerInventory(id, inventory);
}

void zappy::gui::RaylibRenderer::hatchEgg(const int &eggId)
{
    ARenderer::hatchEgg(eggId);
}

void zappy::gui::RaylibRenderer::removeEgg(const int &eggId)
{
    ARenderer::removeEgg(eggId);
}

void zappy::gui::RaylibRenderer::removePlayer(const int &id)
{
    ARenderer::removePlayer(id);
}

void zappy::gui::RaylibRenderer::endGame(const std::string &teamName)
{
    ARenderer::endGame(teamName);
}
