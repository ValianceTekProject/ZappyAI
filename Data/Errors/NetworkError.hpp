/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** NetworkError.hpp
*/

#pragma once

#include "AError.hpp"

namespace zappy {
    namespace network {
        class NetworkError : public AError
        {
            public:
                NetworkError(const std::string &msg, const std::string &where)
                    noexcept : gui::AError(msg, where) {};
        };
    }
}
