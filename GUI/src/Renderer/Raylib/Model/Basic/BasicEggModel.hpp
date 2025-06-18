/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** BasicEggModel.hpp
*/

#pragma once

#include "AEggModel.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class BasicEggModel : public AEggModel {
                public:
                    BasicEggModel(const int &id);
                    ~BasicEggModel() override = default;
    
                    void init() override;
    
                    void update() override;
    
                    void render() override;
    
                private:
                    void _initModel() override;
            };
        }
    }
}