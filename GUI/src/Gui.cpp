/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Gui.cpp
*/

#include "Gui.hpp"

zappy::gui::Gui::Gui() :
    _debug(false),
    _ip("127.0.0.1"),
    _port(4242),
    _protocol(nullptr),
    _gameState(nullptr),
    _renderer(nullptr)
{}

void zappy::gui::Gui::parseArgs(int argc, char const *argv[])
{
    if (argc < 2)
        throw ParsingError("Not enough arguments\n\tUsage: ./zappy_gui -p port -h host", "Parsing");

    if (argc == 2 && std::string(argv[1]) == "-help") {
        std::cout << "Usage: ./zappy_gui -p port -h host" << std::endl;
        exit(0);
    }

    bool raylib = false;

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
        } else if (arg == "-debug" || arg == "-d") {
            _debug = true;
        } else if (arg == "-raylib" || arg == "-r") {
            raylib = true;
        } else
            throw ParsingError("Unknown option: " + arg, "Parsing");
    }

    if (_ip.empty()) {
        throw ParsingError("Host (-h) not specified", "Parsing");
    }
    if (_port <= 0 || _port > 65535) {
        throw ParsingError("Port out of range: " + std::to_string(_port), "Parsing");
    }

    if (_debug) {
        _renderer = std::make_shared<DebugRenderer>();
    } else if (!_renderer) {
        if (raylib)
            _renderer = std::make_shared<RaylibRenderer>();
        else
            _renderer = std::make_shared<NcursesRenderer>();
    }
}

void zappy::gui::Gui::init()
{
    _gameState = std::make_shared<game::GameState>();

    _renderer->setGameState(_gameState);

    _initNetwork();

    while(!_isMapCreated())
        _protocol->update();
}

void zappy::gui::Gui::_initNetwork()
{
    _protocol = std::make_unique<network::Protocol>(_renderer, _gameState, _debug);
    if (!_protocol->connectToServer(_ip, _port))
        throw network::NetworkError("Connection failed", "Network");
}

void zappy::gui::Gui::run()
{
    init();

    _protocol->setTimeUnit(50);

    bool running = true;
    while (running) {
        _renderer->handleInput();

        _protocol->update();
        _renderer->update();

        if (_renderer->shouldClose()) {
            running = false;
            continue;
        }

        _renderer->render();
    }

    _protocol->disconnect();
}
