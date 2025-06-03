/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Server
*/

#include "Server.hpp"
#include "Socket.hpp"
#include "Error/Error.hpp"
#include "Game.hpp"
#include "my_macros.hpp"
#include <memory>

zappy::server::Server::Server(int argc, char const *argv[])
{
    this->_flags = {
        {"-p", [this](int value) {this->_port = value;}},
        {"-x", [this](int value) {this->_width = value;}},
        {"-y", [this](int value) {this->_height = value;}},
        {"-c", [this](int value) {this->_clientNb = value;}},
        {"-f", [this](int value) {this->_freq = value;}}
    };
    this->_parseFlags(argc, argv);
    this->_game = std::make_unique<zappy::game::Game>(this->_width, this->_height);
    this->_socket =
        std::make_unique<server::Socket>(this->_port, this->_clientNb);
    this->_fds.push_back({this->_socket->getSocket(), POLLIN, 0});
    std::cout << "Zappy Server listening on port " << this->_port << "...\n";
}

int handleFlag(const std::string &flag)
{
    std::stringstream stream;
    int res;

    stream << flag;
    stream >> res;
    return res;
}

void zappy::server::Server::_parseName(int &index, char const *argv[])
{
    index += 1;
    while (argv[index]) {
        if (std::string(argv[index]).find("-") == 0)
            break;
        this->_namesTeam.push_back(argv[index]);
        index += 1;
        zappy::game::Team team(argv[index]);
        this->_teamList.push_back(team);
    }

    if (this->_teamList.empty())
        throw error::InvalidArg("Flag -n must have at least on argument !");
    index -= 1;
}

void zappy::server::Server::_parseFlagsInt(int &index, std::string arg, std::string value)
{
    auto flagsIt = this->_flags.find(arg);
    if (flagsIt == this->_flags.end())
        throw error::Error("Missing or invalid value");
    auto valueInt = handleFlag(value);
    flagsIt->second(valueInt);
    index += 1;
}

void zappy::server::Server::_parseFlags(int argc, char const *argv[])
{
    if (argv == nullptr || argv[0] == nullptr)
        throw error::ServerConnection("Unable to access argv");

    for (int i = 1; i < argc; i += 1) {
        if (argv[i] == nullptr)
            throw error::Error("Error in argument list");

        std::string currentArg = argv[i];
        if (currentArg == "-n") {
            this->_parseName(i, argv);
            continue;
        }
        this->_parseFlagsInt(i, currentArg, argv[i + 1]);
    }

    if (this->_port == zappy::noValue || this->_width == zappy::noValue ||
        this->_height == zappy::noValue || this->_clientNb == zappy::noValue ||
        this->_freq == zappy::noValue || this->_namesTeam.empty()) {
        throw error::InvalidArg(
            "Missing arguments: -p -x -y -c -f -n <names>");
    }
}

void zappy::server::Server::runServer()
{
    std::thread networkThread(&zappy::server::Server::runLoop, this);
    std::thread gameThread(&game::Game::gameLoop, this->_game.get());

    networkThread.join();
    gameThread.join();
}
