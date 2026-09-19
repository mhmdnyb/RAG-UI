package com.github.core_server.controller;

import com.github.core_server.exception.UserErrorCode;
import com.github.core_server.exception.UserException;
import com.github.core_server.payload.request.CreateUserRequest;
import com.github.core_server.payload.response.ApiResponse;
import com.github.core_server.payload.response.UserResponse;
import com.github.core_server.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/register")
@RequiredArgsConstructor
public class RegisterController {

    private final UserService userService;

    @PostMapping
    public ApiResponse<UserResponse> register(
            @RequestBody CreateUserRequest request
    ) {

        return userService.createUser(request);
    }
}
