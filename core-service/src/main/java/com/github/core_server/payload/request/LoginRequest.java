package com.github.core_server.payload.request;

import lombok.Getter;

@Getter
public class LoginRequest {
    private String phoneNumber;
    private String password;
}
