/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Observer
*/

#include "Server.hpp"

void zappy::server::Server::attachObserver(std::shared_ptr<zappy::observer::IObserver> observer) {
    _observers.push_back(observer);
}

void zappy::server::Server::notifyObservers(int sig) {
    for (auto &obs : _observers) {
        obs->onNotify(sig);
    }
}
