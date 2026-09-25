package com.github.core_server.payload.response;

import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

@Setter
@Getter
@Builder
public class UserResponse {
    private String phoneNumber;
    private String name;
    private String createdAt;
}
