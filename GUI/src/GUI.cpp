/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** GUI.cpp
*/

#include "GUI.hpp"

gui::ZappyGui::ZappyGui() :
    _ip("127.0.0.1"),
    _port(4242),
    _frequency(100),
    _renderer(nullptr)
{
    // _gameState.setFrequency(_frequency);
}

void gui::ZappyGui::parseArgs(int argc, char const *argv[])
{
    if (argc < 2)
        throw ParsingError("Not enough arguments", "Parsing");
    (void)argv;
}

void gui::ZappyGui::run()
{

}
