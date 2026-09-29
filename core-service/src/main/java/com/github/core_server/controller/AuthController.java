package com.github.core_server.controller;

import com.github.core_server.exception.UserErrorCode;
import com.github.core_server.exception.UserException;
import com.github.core_server.payload.response.ApiResponse;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/auth")
public class AuthController {

    @GetMapping
    public ApiResponse<Void> checkLogin(){

        Authentication currentAuthentication =
                SecurityContextHolder.getContext().getAuthentication();

        if (currentAuthentication != null
                && currentAuthentication.isAuthenticated()
                && !(currentAuthentication instanceof AnonymousAuthenticationToken)) {

            throw new UserException(UserErrorCode.AlreadyAuthenticated);
        }

        return ApiResponse.<Void>builder()
                .status("OK")
                .build();
    }
}
