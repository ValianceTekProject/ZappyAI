/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Server
*/

#include "Server.hpp"
#include "EncapsuledFunction/Socket.hpp"
#include "Error/Error.hpp"
#include "Game.hpp"
#include <memory>

zappy::server::Server::Server(int argc, char const *argv[])
{
    this->_game = std::make_unique<zappy::game::Game>();
    this->_parseArgs(argc, argv);
}

int handlerFlag(char const *argv[], int i, std::string flag)
{
    std::stringstream stream;
    int res = -1;

    if (std::string(argv[i]) == flag && argv[i + 1]) {
        stream << std::string(argv[i + 1]);
        stream >> res;
    }
    return res;
}

void zappy::server::Server::_parseName(int &index, char const *argv[])
{
    int nameCount = 0;

    while (argv[index]) {
        if (std::string(argv[index]).find("-") == 0)
            break;
        _namesTeam.push_back(argv[index]);
        nameCount += 1;
        index += 1;
        zappy::game::Team team(argv[index]);
        _teamList.push_back(team);
    }

    if (nameCount == 0)
        throw error::InvalidArg("Flag -n must have at least on argument !");
}

void zappy::server::Server::_parseArgs(int argc, char const *argv[])
{
    if (argv == nullptr || argv[0] == nullptr)
        throw error::ServerConnection("Unable to access argv");
    for (int i = 1; i < argc; ++i) {
        if (!argv[i])
            throw error::Error("Error in argument list");

        std::string currentArg = argv[i];

        if (currentArg == "-n") {
            ++i;
            _parseName(i, argv);
            --i;
            continue;
        }

        int value = handlerFlag(argv, i, currentArg);
        if (value != -1) {
            if (currentArg == "-p")
                _port = value;
            else if (currentArg == "-x")
                _width = value;
            else if (currentArg == "-y")
                _height = value;
            else if (currentArg == "-c")
                _clientNb = value;
            else if (currentArg == "-f")
                _freq = value;
            i += 1;
        } else
            throw error::InvalidArg(
                "Unknown or badly formatted argument: " + currentArg);
    }

    if (_port == -1 || _width == -1 || _height == -1 || _clientNb == -1 ||
        _freq == -1 || _namesTeam.empty())
        throw error::InvalidArg(
            "Missing arguments: -p -x -y -c -f -n <names>");
}

void zappy::server::Server::runServer()
{
    this->_socket =
        std::make_unique<server::Socket>(this->_port, this->_clientNb);

    std::cout << "Zappy Server listening on port " << this->_port << "...\n";
    fds.push_back({this->_socket->getSocket(), POLLIN, 0});

    std::thread networkThread(&zappy::server::Server::runLoop, this);
    std::thread gameThread(&game::Game::gameLoop, this->_game.get());

    networkThread.join();
    gameThread.join();
}
