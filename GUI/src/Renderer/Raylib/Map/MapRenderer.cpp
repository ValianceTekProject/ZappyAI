/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** MapRenderer.cpp
*/

#include "MapRenderer.hpp"
#include <memory>

zappy::gui::raylib::MapRenderer::MapRenderer(const std::shared_ptr<game::Map> map) :
    _map(map) {}

void zappy::gui::raylib::MapRenderer::init()
{
    // INIT
}
