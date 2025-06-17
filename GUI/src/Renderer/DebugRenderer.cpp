/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** NcursesRenderer.cpp
*/

#include "DebugRenderer.hpp"

zappy::gui::DebugRenderer::DebugRenderer() :
    ARenderer::ARenderer(),
    _shouldClose(false)
{}

void zappy::gui::DebugRenderer::PlayerExpulsion(const int &id)
{
    (void)id;
}

void zappy::gui::DebugRenderer::PlayerBroadcast(const int &id, const std::string &message)
{
    (void)id;
    (void)message;
}

void zappy::gui::DebugRenderer::StartIncantation(
    const int &x, const int &y,
    const int &level,
    const std::vector<int> &playerIds
)
{
    (void)x;
    (void)y;
    (void)level;
    (void)playerIds;
}

void zappy::gui::DebugRenderer::EndIncantation(const int &x, const int &y, const bool &result)
{
    (void)x;
    (void)y;
    (void)result;
}
