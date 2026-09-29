package com.github.core_server.exception;

public enum ConversationErrorCode {

    ConversationNotFound("101", "Conversation not found"),
    ConversationNotOwned("102", "User does not own the conversation");

    private final String code;
    private final String message;

    ConversationErrorCode(String code, String message) {
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
