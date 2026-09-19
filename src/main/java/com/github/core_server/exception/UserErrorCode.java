package com.github.core_server.exception;

public enum UserErrorCode {

    PhoneNumberAlreadyExists("001", "This phone number already exists"),
    AlreadyAuthenticated("002", "User is already Authenticated"),
    UserNotFound("003", "User not found"),
    InvalidLogin("004", "The login is invalid");

    private final String code;
    private final String message;

    UserErrorCode(String code, String message) {
        this.code = code;
        this.message = message;
    }

    public String getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }
}
