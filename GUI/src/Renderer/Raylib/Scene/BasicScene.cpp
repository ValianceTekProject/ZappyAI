/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** BasicScene.cpp
*/

#include "BasicScene.hpp"

zappy::gui::raylib::BasicScene::BasicScene(const std::shared_ptr<game::GameState> &gameState) :
    AScene::AScene(gameState)
{}

void zappy::gui::raylib::BasicScene::init()
{
    AScene::init();
}

void zappy::gui::raylib::BasicScene::handleInput(InputManager &inputManager)
{
    AScene::handleInput(inputManager);
}

void zappy::gui::raylib::BasicScene::update()
{
    AScene::update();
}

void zappy::gui::raylib::BasicScene::render() const
{
    BeginMode3D(getCamera());

    _mapRenderer->render();

    EndMode3D();
}

bool zappy::gui::raylib::BasicScene::shouldClose() const
{
    return WindowShouldClose();
}

void zappy::gui::raylib::BasicScene::addEgg(const int &id)
{
    AScene::addEgg(id);
}

void zappy::gui::raylib::BasicScene::addPlayer(const int &id)
{
    AScene::addPlayer(id);
}

void zappy::gui::raylib::BasicScene::updatePlayerPosition(const int &id, const size_t &x, const size_t &y, const game::Orientation &orientation)
{
    AScene::updatePlayerPosition(id, x, y, orientation);
}

void zappy::gui::raylib::BasicScene::updatePlayerLevel(const int &id, const size_t &level)
{
    AScene::updatePlayerLevel(id, level);
}

void zappy::gui::raylib::BasicScene::updatePlayerInventory(const int &id, const game::Inventory &inventory)
{
    AScene::updatePlayerInventory(id, inventory);
}

void zappy::gui::raylib::BasicScene::hatchEgg(const int &id)
{
    AScene::hatchEgg(id);
}

void zappy::gui::raylib::BasicScene::removeEgg(const int &id)
{
    AScene::removeEgg(id);
}

void zappy::gui::raylib::BasicScene::removePlayer(const int &id)
{
    AScene::removePlayer(id);
}

void zappy::gui::raylib::BasicScene::endGame(const std::string &teamName)
{
    DrawText(TextFormat("Team %s wins!", teamName.c_str()), 10, 10, 20, GREEN);
}
