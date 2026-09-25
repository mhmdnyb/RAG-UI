package com.github.core_server.service;

import com.github.core_server.entity.UserEntity;
import com.github.core_server.exception.UserErrorCode;
import com.github.core_server.exception.UserException;
import com.github.core_server.helper.UserHelper;
import com.github.core_server.mapper.UserMapper;
import com.github.core_server.payload.request.CreateUserRequest;
import com.github.core_server.payload.response.ApiResponse;
import com.github.core_server.payload.response.UserResponse;
import lombok.AllArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@AllArgsConstructor
public class UserService {

    private final UserHelper userHelper;
    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;

    @Transactional
    public ApiResponse<UserResponse> createUser(CreateUserRequest request) {

        if (userHelper.existsByPhoneNumber(request.getPhoneNumber())) {

            throw new UserException(UserErrorCode.PhoneNumberAlreadyExists);
        }

        UserEntity user = userMapper.toEntity(request);

        user.setPassword(passwordEncoder.encode(request.getPassword()));

        userHelper.save(user);

        return ApiResponse.<UserResponse>builder()
                .status("OK")
                .data(userMapper.toUserResponse(user))
                .build();
    }

}
