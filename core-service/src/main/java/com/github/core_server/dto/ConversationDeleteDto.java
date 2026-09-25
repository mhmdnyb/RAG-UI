package com.github.core_server.dto;

public record ConversationDeleteDto(
        Long ConversationId,
        Long userId
) {
}
