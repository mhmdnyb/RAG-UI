package com.github.core_server.payload.request;

import lombok.Getter;

@Getter
public class CreateUserRequest {
    private String name;
    private String phoneNumber;
    private String password;
}
