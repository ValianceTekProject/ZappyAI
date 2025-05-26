//
// EPITECH PROJECT, 2025
// Player
// File description:
// Player
//

#pragma once

#include <functional>
#include <optional>
#include <vector>
#include <string>

namespace ZappyPlayer {
    class User {
        public:
            User();
            ~User();

        private:
    };

    class Team {
        public:
            Team();
            ~Team();

            std::string getName() const { return _name; }
            void setName(const std::string &name) { this->_name = name; }
            
            std::size_t getSize() const {return _size; }
            void setSize(const std::size_t size) { this->_size = size; }

            const std::vector<std::reference_wrapper<User>> getUserList() const {return this->_userList; }
            void addUser(User &user) { this->_userList.push_back(user); }

        private:
            std::string _name;
            std::size_t _size;
            std::vector<std::reference_wrapper<User>> _userList;
    };
}
