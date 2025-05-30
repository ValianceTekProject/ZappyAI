/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Gui.cpp
*/

#include "Gui.hpp"

zappy::gui::Gui::Gui() :
    _ip("127.0.0.1"),
    _port(4242),
    _frequency(100),
    _renderer(nullptr)
{
    _gameState->setFrequency(_frequency);
}

void zappy::gui::Gui::parseArgs(int argc, char const *argv[])
{
    if (argc < 2)
        throw ParsingError("Not enough arguments\n\tUsage: ./zappy_gui -p port -h host", "Parsing");

    if (argc == 2 && std::string(argv[1]) == "-help") {
        std::cout << "Usage: ./zappy_gui -p port -h host" << std::endl;
        exit(0);
    }

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];

        if (arg == "-p") {
            if (i + 1 >= argc)
                throw ParsingError("Missing value for -p", "Parsing");
            std::istringstream ss(argv[++i]);
            if (!(ss >> _port) || !_port)
                throw ParsingError("Invalid port number: " + std::string(argv[i]), "Parsing");
        } else if (arg == "-h") {
            if (i + 1 >= argc)
                throw ParsingError("Missing value for -h", "Parsing");
            _ip = argv[++i];
        } else if (arg == "-gl" || arg == "-opengl") {
            _renderer = std::make_unique<OpenGLRenderer>();
        } else
            throw ParsingError("Unknown option: " + arg, "Parsing");
    }

    if (_ip.empty()) {
        throw ParsingError("Host (-h) not specified", "Parsing");
    }
    if (_port <= 0 || _port > 65535) {
        throw ParsingError("Port out of range: " + std::to_string(_port), "Parsing");
    }

    if (!_renderer)
        _renderer = std::make_unique<NcursesRenderer>();
}

void zappy::gui::Gui::init()
{
    std::cout << "IP: " << _ip << std::endl;
    std::cout << "Port: " << _port << std::endl;

    _gameState = std::make_shared<game::GameState>();

    _renderer->init();
    _renderer->setGameState(_gameState);
}

void zappy::gui::Gui::run()
{
    init();
}
