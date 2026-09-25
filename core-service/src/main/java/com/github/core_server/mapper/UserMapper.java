package com.github.core_server.mapper;

import com.github.core_server.entity.UserEntity;
import com.github.core_server.payload.request.CreateUserRequest;
import com.github.core_server.payload.response.UserResponse;
import com.github.core_server.security.CustomUserDetails;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;

@Component
public class UserMapper {
    public UserDetails toUserDetails(UserEntity user){
        return new CustomUserDetails(user);
    }

    public UserEntity toEntity(CreateUserRequest request){

        return UserEntity.builder()
                .phoneNumber(request.getPhoneNumber())
                .password(request.getPassword())
                .name(request.getName())
                .build();
    }

    public UserResponse toUserResponse(UserEntity user){

        return UserResponse.builder()
                .phoneNumber(user.getPhoneNumber())
                .name(user.getName())
                .createdAt(
                        user.getCreatedAt().toString().substring(0, 10)
                )
                .build();
    }
}
