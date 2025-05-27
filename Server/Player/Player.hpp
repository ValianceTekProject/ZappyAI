//
// EPITECH PROJECT, 2025
// Player
// File description:
// Player
//

#pragma once

#include <functional>
#include <string>
#include <vector>

namespace ZappyPlayer {

    enum class ClientState {
        WAITING_TEAM_NAME,
        CONNECTED,
    };

    class User {
       public:
        User() : _state(ClientState::WAITING_TEAM_NAME) {};
        ~User() = default;

        int getSocket() const { return _socket; }
        void setSocket(int socket) { _socket = socket; }

        ClientState getState() const { return _state; }
        void setState(ClientState state) { _state = state; }

       private:
        int _socket;
        ClientState _state;
    };

    class Team {
       public:
        Team() = default;
        ~Team() = default;

        std::string getName() const { return _name; }

        void setName(const std::string &name) { this->_name = name; }

        std::size_t getSize() const { return _size; }

        void setSize(const std::size_t size) { this->_size = size; }

        std::size_t getSizeMax() const { return _sizeMax; }

        void setSizeMax(const std::size_t size) { this->_sizeMax = size; }

        const std::vector<std::reference_wrapper<User>> getUserList() const
        {
            return this->_userList;
        }

        void addUser(User &user) { this->_userList.push_back(user); }

       private:
        std::string _name;
        std::size_t _size;
        std::size_t _sizeMax;
        std::vector<std::reference_wrapper<User>> _userList;
    };
}
