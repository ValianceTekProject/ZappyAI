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
{}

void zappy::gui::RaylibRenderer::init()
{}

void zappy::gui::RaylibRenderer::handleInput()
{}

void zappy::gui::RaylibRenderer::update()
{}

void zappy::gui::RaylibRenderer::render() const
{}

bool zappy::gui::RaylibRenderer::shouldClose() const
{
    return false;
}

void zappy::gui::RaylibRenderer::addEgg(const int &eggId, const int &fatherId, const size_t &x, const size_t &y)
{
    (void)eggId;
    (void)fatherId;
    (void)x;
    (void)y;
}

void zappy::gui::RaylibRenderer::addPlayer(const game::Player &player)
{
    (void)player;
}

void zappy::gui::RaylibRenderer::updatePlayerPosition(const int &id, const size_t &x, const size_t &y, const game::Orientation &orientation)
{
    (void)id;
    (void)x;
    (void)y;
    (void)orientation;
}

void zappy::gui::RaylibRenderer::updatePlayerLevel(const int &id, const size_t &level)
{
    (void)id;
    (void)level;
}

void zappy::gui::RaylibRenderer::updatePlayerInventory(const int &id, const game::Inventory &inventory)
{
    (void)id;
    (void)inventory;
}

void zappy::gui::RaylibRenderer::hatchEgg(const int &eggId)
{
    (void)eggId;
}

void zappy::gui::RaylibRenderer::removeEgg(const int &eggId)
{
    (void)eggId;
}

void zappy::gui::RaylibRenderer::removePlayer(const int &id)
{
    (void)id;
}

void zappy::gui::RaylibRenderer::endGame(const std::string &teamName)
{
    (void)teamName;
}
