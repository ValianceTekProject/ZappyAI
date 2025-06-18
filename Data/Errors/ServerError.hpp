/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** ServerError copy.hpp
*/

#pragma once

#include "AError.hpp"

namespace zappy {
    namespace server {
        class ServerError : public AError
        {
            public:
                ServerError(const std::string &msg, const std::string &where)
                    noexcept : AError(msg, where) {};
        };
    }
}
