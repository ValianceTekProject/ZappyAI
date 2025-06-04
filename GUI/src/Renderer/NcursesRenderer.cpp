/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** NcursesRenderer.cpp
*/

#include "NcursesRenderer.hpp"

zappy::gui::NcursesRenderer::NcursesRenderer() :
    _shouldClose(false)
{}

void zappy::gui::NcursesRenderer::init()
{
//     _window = initscr();
//     cbreak();
//     noecho();
//     curs_set(0);
//     nodelay(stdscr, TRUE);
}

void zappy::gui::NcursesRenderer::handleInput()
{
    // int ch = getch();
    // if (ch == 'q')
    //     _shouldClose = true;
}

void zappy::gui::NcursesRenderer::update()
{
    // Update game state here
}

void zappy::gui::NcursesRenderer::render() const
{
    // clear();
    // // Render game state here
    // refresh();
}
