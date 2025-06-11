/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** NcursesRenderer.cpp
*/

#include "NcursesRenderer.hpp"

zappy::gui::NcursesRenderer::NcursesRenderer() :
    ARenderer::ARenderer(),
    _shouldClose(false),
    _window(nullptr),
    _help(false)
{}

void zappy::gui::NcursesRenderer::init()
{
    _initWindow();
    _initColors();
}

void zappy::gui::NcursesRenderer::_initWindow()
{
    initscr();
    noecho();
    cbreak();
    keypad(stdscr, TRUE);
    curs_set(0);
    start_color();
    timeout(0);
    _window = stdscr;
}

void zappy::gui::NcursesRenderer::_initColors()
{
    init_pair(1, COLOR_WHITE, COLOR_BLACK);
    init_pair(2, COLOR_GREEN, COLOR_BLACK);
    init_pair(3, COLOR_RED, COLOR_BLACK);
    init_pair(4, COLOR_YELLOW, COLOR_BLACK);
}

void zappy::gui::NcursesRenderer::handleInput()
{
    int ch = getch();
    if (ch == 'q' || ch == 27)
        _shouldClose = true;
    else if (ch == 'h')
        _help = !_help;
}

void zappy::gui::NcursesRenderer::update() {}

void zappy::gui::NcursesRenderer::render() const
{
    werase(_window);
    if (_gameState)
        _drawMap();
    box(_window, 0, 0);
    wrefresh(_window);
}

bool zappy::gui::NcursesRenderer::shouldClose() const
{
    if (_shouldClose) {
        clear();
        endwin();
    }
    return _shouldClose;
}

void zappy::gui::NcursesRenderer::endGame(const std::string &teamName)
{
    _shouldClose = true;
    ARenderer::endGame(teamName);
}

void zappy::gui::NcursesRenderer::_drawMap() const
{
    const auto &map = _gameState->getMap();
    size_t tileHeight = 5;
    size_t tileWidth = 30;

    for (size_t y = 0; y < map.getHeight(); ++y) {
        for (size_t x = 0; x < map.getWidth(); ++x) {
            const auto &tile = map.getTile(x, y);
            const auto eggs = _gameState->getEggsByCoord(x, y);
            const auto players = _gameState->getPlayersByCoord(x, y);
            _drawTile(tile, eggs, players, x, y, 1 + y * tileHeight, 1 + x * tileWidth);
        }
    }
}

void zappy::gui::NcursesRenderer::_drawTile(
    const zappy::game::Tile &tile,
    const std::vector<zappy::game::Egg> &eggs,
    const std::vector<zappy::game::Player> &players,
    size_t, size_t,
    size_t row, size_t col
) const
{
    std::ostringstream playersLine;
    for (const auto &player : players) {
        playersLine << "P" << player.getId() << "(L" << player.level << ") ";
    }

    std::ostringstream resourcesLine;
    for (size_t i = 0; i < zappy::game::RESOURCE_QUANTITY; ++i) {
        size_t count = tile.getResourceQuantity(static_cast<zappy::game::Resource>(i));
        if (count > 0) {
            resourcesLine << zappy::game::names[i].substr(0, 3) << ":" << count << " ";
        }
    }

    std::string playersStr = playersLine.str();
    std::string resourcesStr = resourcesLine.str();

    mvwprintw(_window, row,     col, "+----------------------------+");
    mvwprintw(_window, row + 1, col, "| Eggs: %-3zu                  |", eggs.size());
    mvwprintw(_window, row + 2, col, "| %-26s |", playersStr.substr(0, 26).c_str());
    mvwprintw(_window, row + 3, col, "| %-26s |", resourcesStr.substr(0, 26).c_str());
    mvwprintw(_window, row + 4, col, "+----------------------------+");
}
