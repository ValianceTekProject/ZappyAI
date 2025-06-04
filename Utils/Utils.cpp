/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Signal
*/

#include "Utils.hpp"
#include <stdexcept>
#include "Server.hpp"


zappy::utils::Signal* zappy::utils::Signal::_instance = nullptr;

zappy::utils::Signal::Signal(zappy::server::Server &server, zappy::game::Game &game) : _server(server), _game(game) {}

void zappy::utils::Signal::onNotify(int sig)
{
    stopServer(sig);
}

void zappy::utils::Signal::initSignalHandling(Signal *instance)
{
    _instance = instance;

    my_signal(SIGINT, signalWrapper);
    my_signal(SIGTERM, signalWrapper);
}

void zappy::utils::Signal::my_signal(int sig, sighandler_t handler)
{
    if (signal(sig, handler) == SIG_ERR)
        throw std::runtime_error("Unable to use signal()");
}

void zappy::utils::Signal::signalWrapper(int sig)
{
    if (_instance)
        _instance->stopServer(sig);
}

void zappy::utils::Signal::stopServer(int sig)
{
    std::cout << "Received signal " << sig << ". Closing server..." << std::endl;
    _server.setRunningState(RunningState::STOP);
    _game.setRunningState(RunningState::STOP);
    
    closeClients();
}

void zappy::utils::Signal::closeClients()
{
    _server.clearTeams();
}