/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** BasicResourceModel.hpp
*/

#pragma once

#include "AResourceModel.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class BasicResourceModel : public AResourceModel {
                public:
                    BasicResourceModel(const int &id, const zappy::game::Resource &resourceType);
                    ~BasicResourceModel() override = default;

                    void init() override;
            };
        }
    }
}
